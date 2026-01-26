from flask import Blueprint, request, jsonify
from extensions import db, mail
from models import Order, MenuItem
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from config import Config
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_mail import Message
import random
import string
import os

admin_bp = Blueprint("admin", __name__)

# Store hashed password for admin (computed once on first use)
_admin_password_hash = None

# OTP storage for admin password reset (in production, use Redis or database)
admin_otp_storage = {}

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_admin_otp_email(email, otp):
    """Send OTP via email for admin password reset"""
    try:
        from flask import current_app
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"⚠️  Email not configured. Admin OTP for {email}: {otp}")
            return False
            
        msg = Message(
            subject="Admin Password Reset OTP - Hotel Shanmuga Bhavaan",
            recipients=[email],
            body=f"""
Hello Admin,

You have requested to reset your admin password for Hotel Shanmuga Bhavaan Dashboard.

Your One-Time Password (OTP) is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you did not request this password reset, please secure your account immediately.

Best regards,
Hotel Shanmuga Bhavaan System
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
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 4px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Admin Password Reset</h1>
            <p>Hotel Shanmuga Bhavaan Dashboard</p>
        </div>
        <div class="content">
            <p>Hello Admin,</p>
            <p>You have requested to reset your admin password for the Hotel Shanmuga Bhavaan Dashboard.</p>
            <div class="otp-box">
                <p style="margin: 0; font-size: 14px; color: #666;">Your One-Time Password:</p>
                <div class="otp">{otp}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">Valid for 10 minutes</p>
            </div>
            <p><strong>Important:</strong> Please do not share this code with anyone.</p>
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> If you did not request this password reset, please secure your account immediately.
            </div>
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
        print(f"❌ Failed to send admin OTP email: {str(e)}")
        return False

def get_admin_password_hash():
    """Get or compute the admin password hash"""
    global _admin_password_hash
    if _admin_password_hash is None:
        _admin_password_hash = generate_password_hash(Config.ADMIN_PASSWORD)
    return _admin_password_hash


@admin_bp.route("/register", methods=["POST"])
def register():
    """Admin registration disabled - admin credentials are hardcoded for security"""
    return jsonify({"error": "Admin registration is disabled. Admin credentials are configured by the website owner."}), 403


@admin_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    # Validate against hardcoded admin credentials
    if username != Config.ADMIN_USERNAME:
        return jsonify({"error": "Invalid credentials"}), 401

    if password != Config.ADMIN_PASSWORD:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create access token for admin
    # Identity must be string (JWT spec), use additional_claims for admin details
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
        "access_token": access_token,
        "admin": {
            "admin_id": 1,
            "username": Config.ADMIN_USERNAME,
            "email": Config.ADMIN_EMAIL,
            "role": "Admin",
        },
    })


@admin_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    claims = get_jwt()
    if not claims or claims.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({
        "message": "Token valid",
        "admin": {
            "admin_id": claims.get("admin_id"),
            "username": claims.get("username"),
            "email": claims.get("email"),
            "role": claims.get("role"),
        },
    })


@admin_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_token():
    """Refresh admin access token"""
    claims = get_jwt()
    if not claims or claims.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403
    
    # Create new access token with same claims
    new_token = create_access_token(
        identity="admin_1",
        additional_claims={
            "admin_id": claims.get("admin_id"),
            "username": claims.get("username"),
            "email": claims.get("email"),
            "role": claims.get("role")
        }
    )
    
    return jsonify({
        "access_token": new_token,
        "admin": {
            "admin_id": claims.get("admin_id"),
            "username": claims.get("username"),
            "email": claims.get("email"),
            "role": claims.get("role"),
        },
    })


@admin_bp.route("/change_password", methods=["POST"])
@jwt_required()
def change_password():
    """Password change disabled - admin password is configured by the website owner"""
    claims = get_jwt()
    if not claims or claims.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403
    
    return jsonify({"error": "Password change is disabled. Admin credentials are configured by the website owner through environment variables or config."}), 403


@admin_bp.route("/list", methods=["GET"])
@jwt_required()
def list_admins():
    """List admins - returns only the hardcoded admin"""
    identity = get_jwt_identity()
    if not identity or identity.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403

    return jsonify([{
        "admin_id": 1,
        "username": Config.ADMIN_USERNAME,
        "email": Config.ADMIN_EMAIL,
        "role": "Admin",
        "created_at": None
    }])


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def admin_stats():
    """Admin-only stats endpoint mirroring /api/stats/summary."""
    claims = get_jwt()
    if not claims or claims.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403

    try:
        total_orders = Order.query.count()
        revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        confirmed = Order.query.filter_by(status="Confirmed").count()
        pending = Order.query.filter_by(status="Pending").count()

        # Top dishes by total_orders_count
        top_dishes = MenuItem.query.order_by(MenuItem.total_orders_count.desc()).limit(5).all()

        return jsonify({
            "total_orders": total_orders,
            "revenue": float(revenue),
            "confirmed": confirmed,
            "pending": pending,
            "top_dishes": [
                {"name": d.item_name, "orders": d.total_orders_count or 0}
                for d in top_dishes
            ]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 500


@admin_bp.route("/forgot-password", methods=["POST"])
def admin_forgot_password():
    """Send OTP for admin password reset"""
    try:
        data = request.json or {}
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if the email matches the admin email
        if email != Config.ADMIN_USERNAME:
            return jsonify({"error": "Invalid admin email"}), 404
        
        # Generate OTP
        otp = generate_otp()
        admin_otp_storage[email] = {
            "otp": otp,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Try to send OTP via email
        email_sent = send_admin_otp_email(email, otp)
        
        if email_sent:
            return jsonify({"message": "OTP sent to your admin email"}), 200
        else:
            # Email not configured - print to console for development only
            print("\n" + "="*60)
            print(f"🔐 ADMIN PASSWORD RESET OTP (Development Mode)")
            print(f"📧 Email: {email}")
            print(f"🔢 OTP Code: {otp}")
            print(f"⏰ Valid for: 10 minutes")
            print(f"⚠️  Configure email in .env to stop console logging")
            print("="*60 + "\n")
            
            return jsonify({
                "message": "OTP generated successfully. Check server console for OTP code."
            }), 200
        
    except Exception as e:
        print(f"❌ Error in admin forgot-password: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/verify-otp", methods=["POST"])
def admin_verify_otp():
    """Verify OTP for admin password reset"""
    try:
        data = request.json or {}
        email = data.get("email")
        otp = data.get("otp")
        
        if not email or not otp:
            return jsonify({"error": "Email and OTP are required"}), 400
        
        # Check if the email matches the admin email
        if email != Config.ADMIN_USERNAME:
            return jsonify({"error": "Invalid admin email"}), 404
        
        # Check if OTP exists and is valid
        if email not in admin_otp_storage:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        stored_data = admin_otp_storage[email]
        if datetime.utcnow() > stored_data["expires"]:
            del admin_otp_storage[email]
            return jsonify({"error": "OTP expired"}), 400
        
        if stored_data["otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        return jsonify({"message": "OTP verified successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/reset-password", methods=["POST"])
def admin_reset_password():
    """Reset admin password after OTP verification
    
    Note: This updates the password in memory for the current session.
    To make it permanent, update the ADMIN_PASSWORD in the .env file.
    """
    try:
        data = request.json or {}
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")
        
        if not email or not otp or not new_password:
            return jsonify({"error": "Email, OTP, and new password are required"}), 400
        
        # Check if the email matches the admin email
        if email != Config.ADMIN_USERNAME:
            return jsonify({"error": "Invalid admin email"}), 404
        
        # Verify OTP again
        if email not in admin_otp_storage:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        stored_data = admin_otp_storage[email]
        if datetime.utcnow() > stored_data["expires"]:
            del admin_otp_storage[email]
            return jsonify({"error": "OTP expired"}), 400
        
        if stored_data["otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update the admin password in Config (runtime update)
        # Note: For permanent change, the .env file needs to be updated manually
        Config.ADMIN_PASSWORD = new_password
        
        # Reset the cached password hash
        global _admin_password_hash
        _admin_password_hash = None
        
        # Clear OTP
        del admin_otp_storage[email]
        
        return jsonify({
            "message": "Admin password reset successfully. Note: To make this change permanent across server restarts, update the ADMIN_PASSWORD in the .env file."
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
