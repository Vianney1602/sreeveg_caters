from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, mail
from models import Customer, Order, OrderMenuItem
from datetime import datetime, timedelta
import jwt
import os
import random
import string
from flask_mail import Message

users_bp = Blueprint("users", __name__)

# Secret key for JWT tokens
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")

# OTP storage (in production, use Redis or database)
otp_storage = {}

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP via email"""
    try:
        # Check if mail is configured
        from flask import current_app
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"⚠️  Email not configured. OTP for {email}: {otp}")
            return False
            
        msg = Message(
            subject="Your OTP for Password Reset - Hotel Shanmuga Bhavaan",
            recipients=[email],
            body=f"""
Hello,

You have requested to reset your password for your Hotel Shanmuga Bhavaan account.

Your One-Time Password (OTP) is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you did not request this password reset, please ignore this email.

Best regards,
Hotel Shanmuga Bhavaan Team
            """,
            html=f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #7a0000, #d4af37); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }}
        .otp-box {{ background: #f5f5f5; border: 2px solid #7a0000; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
        .otp {{ font-size: 32px; font-weight: bold; color: #7a0000; letter-spacing: 8px; }}
        .footer {{ background: #f9f9f9; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Hotel Shanmuga Bhavaan</h1>
            <p>Password Reset Request</p>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>You have requested to reset your password for your Hotel Shanmuga Bhavaan account.</p>
            <div class="otp-box">
                <p style="margin: 0; font-size: 14px; color: #666;">Your One-Time Password:</p>
                <div class="otp">{otp}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">Valid for 10 minutes</p>
            </div>
            <p><strong>Important:</strong> Please do not share this code with anyone.</p>
            <p>If you did not request this password reset, please ignore this email or contact our support team.</p>
        </div>
        <div class="footer">
            <p>© 2026 Hotel Shanmuga Bhavaan. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

@users_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone", "")
        
        if not name or not email or not password:
            return jsonify({"error": "Name, email, and password are required"}), 400
        
        # Check if user already exists
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = Customer(
            full_name=name,
            email=email,
            phone_number=phone,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": new_user.customer_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/login", methods=["POST"])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = Customer.query.filter_by(email=email).first()
        if not user or not user.password_hash:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check password
        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            "user_id": user.customer_id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.customer_id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone_number
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/google-login", methods=["POST"])
def google_login():
    """Google OAuth login"""
    try:
        data = request.get_json()
        google_id = data.get("google_id")
        email = data.get("email")
        name = data.get("name")
        
        if not email or not name:
            return jsonify({"error": "Email and name are required"}), 400
        
        # Check if user exists
        user = Customer.query.filter_by(email=email).first()
        
        if not user:
            # Create new user for Google sign-in
            user = Customer(
                full_name=name,
                email=email,
                phone_number=""
            )
            db.session.add(user)
            db.session.commit()
        
        # Generate JWT token
        token = jwt.encode({
            "user_id": user.customer_id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.customer_id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone_number
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Send OTP for password reset"""
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if user exists
        user = Customer.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User with this email not found"}), 404
        
        # Generate OTP
        otp = generate_otp()
        otp_storage[email] = {
            "otp": otp,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Try to send OTP via email
        email_sent = send_otp_email(email, otp)
        
        if email_sent:
            # Email sent successfully - no console logging for security
            return jsonify({"message": "OTP sent to your email"}), 200
        else:
            # Email not configured - print to console for development only
            print("\n" + "="*60)
            print(f"🔐 PASSWORD RESET OTP (Development Mode)")
            print(f"📧 Email: {email}")
            print(f"🔢 OTP Code: {otp}")
            print(f"⏰ Valid for: 10 minutes")
            print(f"⚠️  Configure email in .env to stop console logging")
            print("="*60 + "\n")
            
            return jsonify({
                "message": "OTP generated successfully. Check server console for OTP code."
            }), 200
        
    except Exception as e:
        print(f"❌ Error in forgot-password: {str(e)}")
        return jsonify({"error": str(e)}), 500

@users_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Verify OTP for password reset"""
    try:
        data = request.get_json()
        email = data.get("email")
        otp = data.get("otp")
        
        if not email or not otp:
            return jsonify({"error": "Email and OTP are required"}), 400
        
        # Check if OTP exists and is valid
        if email not in otp_storage:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        stored_data = otp_storage[email]
        if datetime.utcnow() > stored_data["expires"]:
            del otp_storage[email]
            return jsonify({"error": "OTP expired"}), 400
        
        if stored_data["otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        return jsonify({"message": "OTP verified successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset password after OTP verification"""
    try:
        data = request.get_json()
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")
        
        if not email or not otp or not new_password:
            return jsonify({"error": "Email, OTP, and new password are required"}), 400
        
        # Verify OTP again
        if email not in otp_storage:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        stored_data = otp_storage[email]
        if datetime.utcnow() > stored_data["expires"]:
            del otp_storage[email]
            return jsonify({"error": "OTP expired"}), 400
        
        if stored_data["otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update password
        user = Customer.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        # Clear OTP
        del otp_storage[email]
        
        return jsonify({"message": "Password reset successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/change-password", methods=["POST"])
def change_password():
    """Change password with OTP verification"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        data = request.get_json()
        otp = data.get("otp")
        new_password = data.get("new_password")
        
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify OTP
        if user.email not in otp_storage:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        stored_data = otp_storage[user.email]
        if datetime.utcnow() > stored_data["expires"]:
            del otp_storage[user.email]
            return jsonify({"error": "OTP expired"}), 400
        
        if stored_data["otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        # Clear OTP
        del otp_storage[user.email]
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/order-history", methods=["GET"])
def order_history():
    """Get user's order history"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user's orders
        orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_items = OrderMenuItem.query.filter_by(order_id=order.order_id).all()
            items_data = [{
                "item_name": item.menu_item.item_name if item.menu_item else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_order_time
            } for item in order_items]
            
            orders_data.append({
                "order_id": order.order_id,
                "customer_name": order.customer_name,
                "phone_number": order.phone_number,
                "email": order.email,
                "event_type": order.event_type,
                "number_of_guests": order.number_of_guests,
                "event_date": order.event_date,
                "event_time": order.event_time,
                "venue_address": order.venue_address,
                "status": order.status,
                "total_amount": order.total_amount,
                "payment_method": order.payment_method,
                "created_at": order.created_at.isoformat(),
                "items": items_data
            })
        
        return jsonify({"orders": orders_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get user profile"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": user.customer_id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone_number,
                "total_orders": user.total_orders_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/profile", methods=["PUT"])
def update_profile():
    """Update user profile"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        if "name" in data:
            user.full_name = data["name"]
        if "phone" in data:
            user.phone_number = data["phone"]
        
        db.session.commit()
        
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
