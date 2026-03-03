from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Customer, Order, OrderMenuItem, AdminSettings
from datetime import datetime, timedelta
from brevo_mail import send_otp_email
import jwt
import os
import random
import string
import redis

users_bp = Blueprint("users", __name__)

# Secret key for JWT tokens
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")

# Redis client for OTP storage (persistent across workers and restarts)
# NOTE: Redis connection is lazy - only tested when actually used
redis_client = None
try:
    redis_client = redis.StrictRedis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,        # prevent setex/get from blocking forever
        socket_keepalive=True,
        health_check_interval=30
    )
    # Don't test connection here - test will happen when first OTP operation is performed
except Exception as e:
    redis_client = None

# Fallback OTP storage (only used if Redis is unavailable)
otp_storage = {}

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def validate_otp_format(otp):
    """Validate OTP is a 6-digit string"""
    return isinstance(otp, str) and len(otp) == 6 and otp.isdigit()


@users_bp.route("/send-registration-otp", methods=["POST"])
def send_registration_otp():
    """Send OTP for new account registration"""
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        # Check if user already exists
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400
            
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with registration prefix
        otp_key = f"reg_otp:{email}"
        if redis_client:
            try:
                redis_client.setex(otp_key, 600, otp)
            except:
                otp_storage[otp_key] = {
                    "otp": otp,
                    "expires": datetime.utcnow() + timedelta(minutes=10)
                }
        else:
            otp_storage[otp_key] = {
                "otp": otp,
                "expires": datetime.utcnow() + timedelta(minutes=10)
            }
            
        # Send OTP email in background (non-blocking) so response is instant
        from brevo_mail import send_registration_otp_email_async
        send_registration_otp_email_async(email, otp)
        
        print(f"[OTP] Registration OTP dispatched for {email}")
        return jsonify({
            "message": "OTP sent successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/register", methods=["POST"])
def register():
    """Register a new user with OTP verification"""
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone", "")
        otp = data.get("otp")
        
        if not name or not email or not password or not otp:
            return jsonify({"error": "All fields including OTP are required"}), 400
            
        # Verify OTP
        otp_key = f"reg_otp:{email}"
        is_valid = False
        
        if redis_client:
            try:
                stored_otp = redis_client.get(otp_key)
                if stored_otp and stored_otp == otp:
                    is_valid = True
                    redis_client.delete(otp_key)
            except:
                pass
                
        if not is_valid and otp_key in otp_storage:
            stored_data = otp_storage[otp_key]
            if datetime.utcnow() <= stored_data["expires"] and stored_data["otp"] == otp:
                is_valid = True
                del otp_storage[otp_key]
                
        if not is_valid:
            return jsonify({"error": "Invalid or expired OTP"}), 400
            
        # Check if user already exists (double check)
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
            "user": {
                "id": new_user.customer_id,
                "name": new_user.full_name,
                "email": new_user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/login", methods=["POST"])
def login():
    """User login - also handles admin login from the same page"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # First, check if this is an admin login
        from config import Config
        from flask_jwt_extended import create_access_token
        from models import AdminSettings
        
        # Check if email matches admin username
        if email == Config.ADMIN_USERNAME or email == Config.ADMIN_EMAIL:
            admin_verified = False
            
            # Try to authenticate: either database hash OR the env-default password
            admin_settings = AdminSettings.query.filter_by(admin_id=1).first()
            if admin_settings and admin_settings.password_hash:
                if check_password_hash(admin_settings.password_hash, password):
                    admin_verified = True
            
            # Always allow fallback to env password (acts as a master password)
            if not admin_verified and password == Config.ADMIN_PASSWORD:
                admin_verified = True
            
            if admin_verified:
                # Admin login successful - create admin token
                access_token = create_access_token(
                    identity="admin_1",
                    additional_claims={
                        "admin_id": 1,
                        "username": Config.ADMIN_USERNAME,
                        "email": Config.ADMIN_EMAIL,
                        "role": "Admin"
                    }
                )
                
                return jsonify({
                    "message": "Login successful",
                "token": access_token,
                "isAdmin": True,
                "user": {
                    "id": 1,
                    "name": "Admin",
                    "email": Config.ADMIN_EMAIL,
                    "role": "Admin"
                }
            }), 200
        
        # Regular user login
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
            "isAdmin": False,
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
        # Store OTP in Redis with 10-minute expiry (600 seconds)
        if redis_client:
            try:
                redis_client.setex(f"otp:{email}", 600, otp)
            except Exception as e:
                otp_storage[email] = {
                    "otp": otp,
                    "expires": datetime.utcnow() + timedelta(minutes=10)
                }
        else:
            # Fallback to in-memory storage if Redis unavailable
            otp_storage[email] = {
                "otp": otp,
                "expires": datetime.utcnow() + timedelta(minutes=10)
            }
        
        # Send OTP email in background (non-blocking) so response is instant
        from brevo_mail import send_otp_email_async
        send_otp_email_async(email, otp)
        
        print(f"[OTP] Password reset OTP dispatched for {email}")
        return jsonify({"message": "OTP sent to your email"}), 200
        
    except Exception as e:
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
        
        # Validate OTP format (must be 6 digits)
        if not validate_otp_format(otp):
            return jsonify({"error": "Invalid OTP format"}), 400
        
        # Check if OTP exists and is valid
        if redis_client:
            try:
                stored_otp = redis_client.get(f"otp:{email}")
                if not stored_otp:
                    return jsonify({"error": "OTP not found or expired"}), 400
                if stored_otp != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
            except Exception as e:
                # Fallback to in-memory if Redis fails
                if email not in otp_storage:
                    return jsonify({"error": "OTP not found or expired"}), 400
                stored_data = otp_storage[email]
                if datetime.utcnow() > stored_data["expires"]:
                    del otp_storage[email]
                    return jsonify({"error": "OTP expired"}), 400
                if stored_data["otp"] != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
        else:
            # Fallback to in-memory storage if Redis unavailable
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
        
        # Validate OTP format (must be 6 digits)
        if not validate_otp_format(otp):
            return jsonify({"error": "Invalid OTP format"}), 400
        
        # Verify OTP again
        if redis_client:
            try:
                stored_otp = redis_client.get(f"otp:{email}")
                if not stored_otp:
                    return jsonify({"error": "OTP not found or expired"}), 400
                if stored_otp != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
            except Exception as e:
                # Fallback to in-memory if Redis fails
                if email not in otp_storage:
                    return jsonify({"error": "OTP not found or expired"}), 400
                stored_data = otp_storage[email]
                if datetime.utcnow() > stored_data["expires"]:
                    del otp_storage[email]
                    return jsonify({"error": "OTP expired"}), 400
                if stored_data["otp"] != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
        else:
            # Fallback to in-memory storage if Redis unavailable
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
        
        # Clear OTP from both Redis and fallback storage
        if redis_client:
            try:
                redis_client.delete(f"otp:{email}")
            except Exception as e:
                pass
        
        if email in otp_storage:
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
        
        # Validate OTP format (must be 6 digits)
        if not validate_otp_format(otp):
            return jsonify({"error": "Invalid OTP format"}), 400
        
        # Verify OTP from both Redis and fallback storage
        if redis_client:
            try:
                stored_otp = redis_client.get(f"otp:{user.email}")
                if not stored_otp:
                    return jsonify({"error": "OTP not found or expired"}), 400
                if stored_otp != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
            except Exception as e:
                # Fallback to in-memory if Redis fails
                if user.email not in otp_storage:
                    return jsonify({"error": "OTP not found or expired"}), 400
                stored_data = otp_storage[user.email]
                if datetime.utcnow() > stored_data["expires"]:
                    del otp_storage[user.email]
                    return jsonify({"error": "OTP expired"}), 400
                if stored_data["otp"] != otp:
                    return jsonify({"error": "Invalid OTP"}), 400
        else:
            # Fallback to in-memory storage if Redis unavailable
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
        
        # Clear OTP from both Redis and fallback storage
        if redis_client:
            try:
                redis_client.delete(f"otp:{user.email}")
            except Exception as e:
                pass
        
        if user.email in otp_storage:
            del otp_storage[user.email]
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============ ADMIN PASSWORD MANAGEMENT ============

@users_bp.route("/admin/change-password", methods=["POST"])
def admin_change_password():
    """Admin change password (when already logged in)"""
    try:
        from config import Config
        from models import AdminSettings
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Verify admin token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("role") != "Admin":
                return jsonify({"error": "Admin access required"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        if not current_password or not new_password:
            return jsonify({"error": "Current and new passwords are required"}), 400
        
        # Verify current password
        admin_settings = AdminSettings.query.filter_by(admin_id=1).first()
        password_is_valid = False
        
        if admin_settings and admin_settings.password_hash:
            # Password in database
            password_is_valid = check_password_hash(admin_settings.password_hash, current_password)
        else:
            # Check default password from env
            from config import Config
            password_is_valid = current_password == Config.ADMIN_PASSWORD
        
        if not password_is_valid:
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Update password in database
        if not admin_settings:
            admin_settings = AdminSettings(admin_id=1, email=Config.ADMIN_EMAIL)
        
        admin_settings.password_hash = generate_password_hash(new_password)
        db.session.add(admin_settings)
        db.session.commit()
        
        return jsonify({"message": "Admin password changed successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/admin/forgot-password", methods=["POST"])
def admin_forgot_password():
    """Admin forgot password - send OTP to admin email"""
    try:
        from config import Config
        
        data = request.get_json(force=True, silent=True) or {}
        email = data.get("email")
        
        
        # If the email doesn't match admin email, return 404 so frontend falls back to user reset flow
        if not email or email.strip().lower() != Config.ADMIN_EMAIL.lower():
            return jsonify({"error": "Not an admin email"}), 404


        # Generate OTP
        otp = generate_otp()
        admin_key = f"admin:{Config.ADMIN_EMAIL}"
        
        # 1. ALWAYS store in memory fallback first for maximum robustness
        otp_storage[admin_key] = {
            "otp": otp,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # 2. Also try to store in Redis if available
        if redis_client:
            try:
                redis_client.setex(f"otp:{admin_key}", 600, otp)
            except Exception as e:
                pass
        
        # Send OTP via email in background (non-blocking)
        from brevo_mail import send_admin_otp_email
        import threading
        def _send_admin_otp():
            try:
                result = send_admin_otp_email(Config.ADMIN_EMAIL, otp)
                if result:
                    print(f"[OTP] Admin OTP email sent OK to {Config.ADMIN_EMAIL}")
                else:
                    print(f"[OTP] Admin OTP email FAILED for {Config.ADMIN_EMAIL}")
            except Exception as exc:
                print(f"[OTP] Admin OTP email error: {exc}")
        threading.Thread(target=_send_admin_otp, daemon=True).start()

        return jsonify({
            "message": "OTP sent to admin email",
            "email_sent": True
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500



@users_bp.route("/admin/verify-otp", methods=["POST"])
def admin_verify_otp():
    """Verify admin OTP"""
    try:
        from config import Config
        admin_email = Config.ADMIN_EMAIL
        admin_key = f"admin:{admin_email}"
        
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        otp = data.get("otp")
        
        if not otp:
            return jsonify({"error": "OTP is required"}), 400
        
        
        # 1. Try memory storage first (as it's now always set)
        if admin_key in otp_storage:
            stored_data = otp_storage[admin_key]
            if datetime.utcnow() > stored_data["expires"]:
                del otp_storage[admin_key]
                return jsonify({"error": "OTP has expired"}), 400
            
            if str(stored_data["otp"]) == str(otp):
                return jsonify({"message": "Admin OTP verified successfully"}), 200
            else:
                pass
        
        # 2. Try Redis if memory failed or didn't have it
        if redis_client:
            try:
                stored_otp = redis_client.get(f"otp:{admin_key}")
                if stored_otp and str(stored_otp) == str(otp):
                    return jsonify({"message": "Admin OTP verified successfully"}), 200
                elif stored_otp:
                    pass
            except Exception as e:
                pass
        
        return jsonify({"error": "OTP not found or expired"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@users_bp.route("/admin/reset-password", methods=["POST"])
def admin_reset_password():
    """Admin reset password after OTP verification"""
    try:
        from config import Config
        from models import AdminSettings
        admin_email = Config.ADMIN_EMAIL
        admin_key = f"admin:{admin_email}"
        
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        
        otp = data.get("otp")
        new_password = data.get("new_password")
        
        if not otp or not new_password:
            return jsonify({"error": "OTP and new_password are required"}), 400
        
        
        # 1. Verify OTP from memory first
        is_verified = False
        if admin_key in otp_storage:
            stored_data = otp_storage[admin_key]
            if datetime.utcnow() <= stored_data["expires"] and str(stored_data["otp"]) == str(otp):
                is_verified = True
        
        # 2. Try Redis if memory failed
        if not is_verified and redis_client:
            try:
                stored_otp = redis_client.get(f"otp:{admin_key}")
                if stored_otp and str(stored_otp) == str(otp):
                    is_verified = True
            except Exception as e:
                pass
        
        if not is_verified:
            return jsonify({"error": "OTP is invalid or has expired. Please request a new one."}), 400
        
        # Update admin password in database
        admin_settings = AdminSettings.query.filter_by(admin_id=1).first()
        if not admin_settings:
            admin_settings = AdminSettings(admin_id=1, email=admin_email)
        
        admin_settings.password_hash = generate_password_hash(new_password)
        db.session.add(admin_settings)
        db.session.commit()
        
        # Clear OTP from both storages
        if admin_key in otp_storage:
            del otp_storage[admin_key]
        if redis_client:
            try:
                redis_client.delete(f"otp:{admin_key}")
            except:
                pass
        
        return jsonify({"message": "Admin password reset successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal reset error: {str(e)}"}), 500

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
