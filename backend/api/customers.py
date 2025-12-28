
from flask import Blueprint, request, jsonify
from extensions import db
from models import Customer, Order
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from config import Config

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/", methods=["GET"])
@jwt_required()
def get_customers():
    claims = get_jwt()
    if not claims or claims.get("role") != "Admin":
        return jsonify({"error": "Forbidden"}), 403
    
    # Get all customers with their order information
    customers = Customer.query.all()
    customer_list = []
    
    for c in customers:
        # Count actual orders for this customer
        orders_count = Order.query.filter_by(customer_id=c.customer_id).count()
        
        # Get total spent
        orders = Order.query.filter_by(customer_id=c.customer_id).all()
        total_spent = sum([o.total_amount or 0 for o in orders])
        
        customer_data = {
            "customer_id": c.customer_id,
            "full_name": c.full_name,
            "phone_number": c.phone_number,
            "email": c.email,
            "total_orders_count": orders_count,
            "total_spent": round(total_spent, 2),
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "is_registered": bool(c.password_hash)
        }
        customer_list.append(customer_data)
    
    return jsonify(customer_list)


@customers_bp.route("/register", methods=["POST"])
def register_customer():
    data = request.json or {}
    full_name = data.get("full_name")
    phone = data.get("phone_number")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not phone or not email or not password:
        return jsonify({"error": "full_name, phone_number, email and password required"}), 400

    existing = Customer.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    # create customer (ensure password is hashed)
    pw_hash = generate_password_hash(password)
    new_customer = Customer(
        full_name=full_name,
        phone_number=phone,
        email=email,
        password_hash=pw_hash
    )
    db.session.add(new_customer)
    db.session.commit()

    # Associate previous orders (placed before signup) by matching email
    try:
        Order.query.filter_by(email=email).update({"customer_id": new_customer.customer_id})
        db.session.commit()
    except Exception:
        db.session.rollback()

    access_token = create_access_token(identity={"customer_id": new_customer.customer_id, "email": new_customer.email})

    return jsonify({"message": "Customer registered", "customer_id": new_customer.customer_id, "access_token": access_token}), 201


@customers_bp.route("/login", methods=["POST"])
def login_customer():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    customer = Customer.query.filter_by(email=email).first()
    if not customer or not customer.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(customer.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"customer_id": customer.customer_id, "email": customer.email})

    return jsonify({"access_token": access_token, "customer": {"customer_id": customer.customer_id, "full_name": customer.full_name, "email": customer.email, "phone_number": customer.phone_number}})


@customers_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_token():
    """Refresh customer access token"""
    identity = get_jwt_identity()
    if not identity or not isinstance(identity, dict) or not identity.get("customer_id"):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Create new access token with same identity
    new_token = create_access_token(identity=identity)
    
    # Get customer info
    customer = Customer.query.get(identity.get("customer_id"))
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    return jsonify({
        "access_token": new_token,
        "customer": {
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone_number": customer.phone_number
        }
    })


@customers_bp.route("/<int:customer_id>/orders", methods=["GET"])
@jwt_required()
def get_customer_orders(customer_id):
    # ensure the token identity matches the requested customer id
    identity = get_jwt_identity()
    if not identity:
        return jsonify({"error": "Unauthorized"}), 401

    token_customer_id = identity.get("customer_id")
    if token_customer_id != customer_id:
        return jsonify({"error": "Forbidden"}), 403

    orders = Order.query.filter_by(customer_id=customer_id).all()
    return jsonify([{
        "order_id": o.order_id,
        "customer_name": o.customer_name,
        "phone": o.phone_number,
        "email": o.email,
        "event": o.event_type,
        "guests": o.number_of_guests,
        "date": o.event_date,
        "time": o.event_time,
        "venue": o.venue_address,
        "status": o.status,
        "total_amount": o.total_amount
    } for o in orders])

@customers_bp.route("/", methods=["POST"])
def add_customer():
    data = request.json
    new_customer = Customer(
        full_name=data["full_name"],
        phone_number=data["phone_number"],
        email=data.get("email")
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer added"}), 201

@customers_bp.route("/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    data = request.json
    customer.full_name = data.get("full_name", customer.full_name)
    customer.phone_number = data.get("phone_number", customer.phone_number)
    customer.email = data.get("email", customer.email)
    
    db.session.commit()
    return jsonify({"message": "Customer updated"})

@customers_bp.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"})
