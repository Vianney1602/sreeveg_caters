from flask import Blueprint, request, jsonify, current_app
import razorpay
from extensions import db, socketio, emit_with_namespace
from models import Order, Customer
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import base64
import hmac
import hashlib

# Configure requests session with retry logic and Google DNS
# This bypasses Eventlet's broken greendns on EC2 ap-south-2
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

payments_bp = Blueprint("payments", __name__)

# Direct Razorpay API calls using subprocess curl (GUARANTEED to work with system DNS)
def create_razorpay_order_direct(amount_paisa, receipt):
    """
    Create Razorpay order using subprocess curl.
    Bypasses Python's socket layer which is corrupted by Eventlet's monkey_patch.
    Uses system's curl which respects /etc/systemd/resolved.conf DNS settings.
    """
    import subprocess
    import json
    
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        raise ValueError("Razorpay keys not configured")
    
    url = "https://api.razorpay.com/v1/orders"
    
    payload = {
        "amount": amount_paisa,
        "currency": "INR",
        "receipt": receipt,
        "payment_capture": 1
    }
    
    print(f"[RAZORPAY] Step 1: Preparing curl request to {url}")
    print(f"[RAZORPAY] Step 2: Payload = {payload}")
    
    try:
        print(f"[RAZORPAY] Step 3: Executing curl subprocess...")
        
        # Use curl via subprocess - guaranteed to use system DNS
        cmd = [
            "curl",
            "-X", "POST",
            url,
            "-u", f"{key_id}:{key_secret}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
            "--max-time", "15",
            "--silent"
        ]
        
        print(f"[RAZORPAY] Step 4: Running curl command...")
        result = subprocess.run(cmd, capture_output=True, timeout=20, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            print(f"[RAZORPAY] ❌ CURL ERROR (code {result.returncode}): {error_msg}")
            raise Exception(f"Curl failed: {error_msg}")
        
        print(f"[RAZORPAY] Step 5: Parsing response...")
        response_data = json.loads(result.stdout)
        print(f"[RAZORPAY] Step 6: ✅ Response received")
        
        return response_data
        
    except subprocess.TimeoutExpired:
        print(f"[RAZORPAY] ❌ TIMEOUT: Curl exceeded 15 seconds")
        raise Exception("Razorpay API timeout")
    except json.JSONDecodeError as e:
        print(f"[RAZORPAY] ❌ JSON ERROR: {str(e)}")
        raise Exception(f"Invalid JSON from Razorpay: {result.stdout}")
    except Exception as e:
        print(f"[RAZORPAY] ❌ ERROR: {type(e).__name__}: {str(e)}")
        raise

def verify_payment_signature_direct(razorpay_order_id, payment_id, razorpay_signature):
    """
    Verify Razorpay payment signature using direct HMAC (bypasses Client library).
    """
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_secret:
        raise ValueError("Razorpay key secret not configured")
    
    # Razorpay signature verification
    data = f"{razorpay_order_id}|{payment_id}"
    generated_signature = hmac.new(
        key_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if generated_signature != razorpay_signature:
        raise ValueError("Invalid payment signature")
    
    return True

def get_razorpay_client():
    """Fallback: traditional razorpay.Client (only for verify utility if needed)"""
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise ValueError("Razorpay keys not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables.")
    return razorpay.Client(auth=(key_id, key_secret))

# DIAGNOSTIC ENDPOINT
@payments_bp.route("/test_dns", methods=["GET"])
def test_dns():
    """Test DNS resolution to api.razorpay.com using curl"""
    import subprocess
    
    results = {}
    
    try:
        print("[DNS_TEST] Testing curl to Razorpay...")
        result = subprocess.run(
            ["curl", "-I", "https://api.razorpay.com", "--max-time", "5"],
            capture_output=True,
            timeout=7,
            text=True
        )
        if result.returncode == 0:
            results["curl_to_api.razorpay.com"] = f"✅ SUCCESS: HTTP connection established"
        else:
            results["curl_to_api.razorpay.com"] = f"❌ FAILED: {result.stderr}"
    except Exception as e:
        results["curl_to_api.razorpay.com"] = f"❌ FAILED: {str(e)}"
    
    try:
        print("[DNS_TEST] Testing nslookup...")
        result = subprocess.run(
            ["nslookup", "api.razorpay.com"],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0 and "Address" in result.stdout:
            results["nslookup"] = f"✅ SUCCESS: DNS resolved"
        else:
            results["nslookup"] = f"❌ FAILED: {result.stderr}"
    except Exception as e:
        results["nslookup"] = f"❌ FAILED: {str(e)}"
    
    print(f"[DNS_TEST] Results: {results}")
    return jsonify(results)

@payments_bp.route("/create_order", methods=["POST"])
def create_razorpay_order():
    try:
        data = request.json
        order_id = data.get("order_id")
        amount = data.get("amount")  # in rupees

        print(f"\n[RAZORPAY] Creating Razorpay order for db_order_id={order_id}, amount={amount}")

        if not order_id or not amount:
            print(f"[RAZORPAY] ERROR: Missing order_id or amount")
            return jsonify({"error": "order_id and amount required"}), 400

        # Verify order exists
        order = Order.query.get(order_id)
        if not order:
            print(f"[RAZORPAY] ERROR: Order {order_id} not found in database")
            return jsonify({"error": "Order not found"}), 404

        print(f"[RAZORPAY] Order found: {order.customer_name}, email: {order.email}")

        # Create Razorpay order using DIRECT requests (bypasses Eventlet DNS)
        try:
            amount_paisa = int(amount * 100)  # in paisa
            receipt = f"order_{order_id}"
            
            print(f"[RAZORPAY] Creating order with amount={amount_paisa} paisa, receipt={receipt}")
            rzp_order = create_razorpay_order_direct(amount_paisa, receipt)
            print(f"[RAZORPAY] ✅ Order created successfully: {rzp_order['id']}")

            # Update order with razorpay_order_id
            order.razorpay_order_id = rzp_order["id"]
            db.session.commit()
            
            current_app.logger.info(f"Razorpay order created: {rzp_order['id']} for order {order_id}")
            print(f"[RAZORPAY] Order {order_id} updated with razorpay_order_id")

            return jsonify({
                "order_id": rzp_order["id"],
                "amount": rzp_order["amount"],
                "currency": rzp_order["currency"]
            })
        except Exception as e:
            print(f"[RAZORPAY] ❌ ERROR creating Razorpay order: {str(e)}")
            current_app.logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": "Payment order creation failed",
                "details": str(e)
            }), 500
    except Exception as e:
        print(f"[RAZORPAY] ❌ ERROR in create_razorpay_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Payment order creation failed",
            "details": str(e)
        }), 500

@payments_bp.route("/verify", methods=["POST"])
def verify_payment():
    data = request.json
    payment_id = data.get("payment_id") if data else None
    order_id = data.get("order_id") if data else None
    razorpay_order_id = data.get("razorpay_order_id") if data else None
    razorpay_signature = data.get("razorpay_signature") if data else None

    print(f"\n[RAZORPAY_VERIFY] Verifying payment: payment_id={payment_id}, razorpay_order_id={razorpay_order_id}")

    if not all([payment_id, order_id, razorpay_order_id, razorpay_signature]):
        print(f"[RAZORPAY_VERIFY] ERROR: Missing payment details")
        return jsonify({"error": "All payment details required"}), 400

    # Verify signature using DIRECT HMAC (bypasses Eventlet DNS issues)
    try:
        print(f"[RAZORPAY_VERIFY] Verifying signature with HMAC")
        verify_payment_signature_direct(razorpay_order_id, payment_id, razorpay_signature)
        print(f"[RAZORPAY_VERIFY] ✅ Signature verified successfully")

        # Update order status to paid
        order = Order.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if order:
            previous_status = order.status or "Pending"
            print(f"[RAZORPAY_VERIFY] Order found: {order.order_id}, current status: {previous_status}")
            
            if previous_status == "Paid":
                print(f"[RAZORPAY_VERIFY] Order already paid")
                return jsonify({"message": "Payment already verified"}), 200

            order.status = "Paid"
            db.session.commit()
            print(f"[RAZORPAY_VERIFY] Order status updated to Paid")
            current_app.logger.info(f"Payment verified for order {order.order_id}")

            # Trigger confirmation email
            from api.orders import trigger_order_confirmation_email
            trigger_order_confirmation_email(order.order_id)

            # Emit real-time status change so admin dashboard updates immediately
            try:
                payload = {
                    'order_id': order.order_id,
                    'customer_id': order.customer_id,
                    'old_status': previous_status,
                    'new_status': 'Paid',
                    'customer_name': order.customer_name,
                    'timestamp': order.updated_at.isoformat() if order.updated_at else None
                }
                socketio.start_background_task(emit_with_namespace, 'order_status_changed', payload, room='admins')
                socketio.start_background_task(emit_with_namespace, 'order_status_changed', payload)
            except Exception:
                pass

            # If this is the customer's first successful (paid) order, broadcast customer_created
            if order.customer_id:
                customer = Customer.query.get(order.customer_id)
                if customer:
                    try:
                        orders_for_customer = Order.query.filter_by(customer_id=order.customer_id).all()
                        total_spent = sum((o.total_amount or 0) for o in orders_for_customer)
                        orders_count = len(orders_for_customer)

                        customer.total_orders_count = orders_count
                        db.session.commit()

                        is_guest = not bool(customer.password_hash)
                        if is_guest and orders_count == 1:
                            payload = {
                                "customer_id": customer.customer_id,
                                "full_name": customer.full_name,
                                "phone_number": customer.phone_number,
                                "email": customer.email,
                                "total_orders_count": orders_count,
                                "total_spent": float(total_spent),
                                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                                "is_registered": False,
                            }
                            socketio.start_background_task(emit_with_namespace, 'customer_created', payload, room='admins')
                    except Exception:
                        current_app.logger.warning("Failed to emit customer_created after payment", exc_info=True)

        return jsonify({"message": "Payment verified successfully"})
    except razorpay.errors.SignatureVerificationError as e:
        print(f"[RAZORPAY_VERIFY] ERROR: Signature verification failed: {str(e)}")
        current_app.logger.warning(f"Payment signature verification failed for {razorpay_order_id}: {str(e)}")
        return jsonify({"error": "Payment verification failed"}), 400
    except Exception as e:
        print(f"[RAZORPAY_VERIFY] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Payment verification error: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Payment verification error",
            "details": str(e)
        }), 500