from flask import Blueprint, request, jsonify
from extensions import db
from models import Order, MenuItem
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from config import Config
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__)

# Store hashed password for admin (computed once on first use)
_admin_password_hash = None

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
