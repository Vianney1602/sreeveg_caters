from flask import Blueprint, request, jsonify, current_app
import razorpay
from extensions import db
from models import Order
import os

payments_bp = Blueprint("payments", __name__)

# Razorpay client - use environment variables for security
def get_razorpay_client():
    key_id = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_RrmurNVGRTmBXH")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "PfJWZVq1dgo4e0vaOoyVdS3K")
    return razorpay.Client(auth=(key_id, key_secret))

@payments_bp.route("/create_order", methods=["POST"])
def create_razorpay_order():
    data = request.json
    order_id = data.get("order_id")
    amount = data.get("amount")  # in rupees

    if not order_id or not amount:
        return jsonify({"error": "order_id and amount required"}), 400

    # Verify order exists
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Create Razorpay order
    try:
        rzp_client = get_razorpay_client()
        rzp_order = rzp_client.order.create({
            "amount": int(amount * 100),  # in paisa
            "currency": "INR",
            "receipt": f"order_{order_id}",
            "payment_capture": 1
        })

        # Update order with razorpay_order_id
        order.razorpay_order_id = rzp_order["id"]
        db.session.commit()
        
        current_app.logger.info(f"Razorpay order created: {rzp_order['id']} for order {order_id}")

        return jsonify({
            "order_id": rzp_order["id"],
            "amount": rzp_order["amount"],
            "currency": rzp_order["currency"]
        })
    except Exception as e:
        current_app.logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
        return jsonify({"error": "Payment order creation failed"}), 500

@payments_bp.route("/verify", methods=["POST"])
def verify_payment():
    data = request.json
    payment_id = data.get("payment_id")
    order_id = data.get("order_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")

    if not all([payment_id, order_id, razorpay_order_id, razorpay_signature]):
        return jsonify({"error": "All payment details required"}), 400

    # Verify signature
    try:
        rzp_client = get_razorpay_client()
        rzp_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": razorpay_signature
        })

        # Update order status to paid
        order = Order.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if order:
            order.status = "Paid"
            db.session.commit()
            current_app.logger.info(f"Payment verified for order {order.order_id}")

        return jsonify({"message": "Payment verified successfully"})
    except razorpay.errors.SignatureVerificationError:
        current_app.logger.warning(f"Payment signature verification failed for {razorpay_order_id}")
        return jsonify({"error": "Payment verification failed"}), 400
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {str(e)}", exc_info=True)
        return jsonify({"error": "Payment verification error"}), 500