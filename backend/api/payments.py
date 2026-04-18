from flask import Blueprint, request, jsonify, current_app
import razorpay
from extensions import db, socketio, emit_with_namespace
from models import Order, Customer
import os

payments_bp = Blueprint("payments", __name__)

# Razorpay client - use environment variables for security (LIVE MODE)
def get_razorpay_client():
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise ValueError("Razorpay keys not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables.")
    return razorpay.Client(auth=(key_id, key_secret))

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

        # Create Razorpay order
        try:
            rzp_client = get_razorpay_client()
            print(f"[RAZORPAY] Razorpay client created")
            
            rzp_order_data = {
                "amount": int(amount * 100),  # in paisa
                "currency": "INR",
                "receipt": f"order_{order_id}",
                "payment_capture": 1
            }
            print(f"[RAZORPAY] Creating order with data: {rzp_order_data}")
            
            rzp_order = rzp_client.order.create(rzp_order_data)
            print(f"[RAZORPAY] Order created successfully: {rzp_order['id']}")

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
            print(f"[RAZORPAY] ERROR creating Razorpay order: {str(e)}")
            current_app.logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": "Payment order creation failed",
                "details": str(e)
            }), 500
    except Exception as e:
        print(f"[RAZORPAY] ERROR in create_razorpay_order: {str(e)}")
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

    # Verify signature
    try:
        rzp_client = get_razorpay_client()
        print(f"[RAZORPAY_VERIFY] Verifying signature with Razorpay")
        
        rzp_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": razorpay_signature
        })
        print(f"[RAZORPAY_VERIFY] Signature verified successfully")

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
        return jsonify({"error": "Payment cancel error"}), 500