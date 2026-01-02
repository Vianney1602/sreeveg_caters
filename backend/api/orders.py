from flask import Blueprint, request, jsonify
from extensions import db, socketio
from models import Order, OrderMenuItem, Customer, MenuItem
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.orm import joinedload

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/", methods=["GET"])
@jwt_required()
def get_orders():
    try:
        claims = get_jwt()
        if not claims or claims.get("role") != "Admin":
            return jsonify({"error": "Forbidden"}), 403
        
        # Use joinedload to eagerly load relationships
        orders = Order.query.options(
            joinedload(Order.menu_items).joinedload(OrderMenuItem.menu_item)
        ).all()
        
        return jsonify([{
            "order_id": o.order_id,
            "customer_name": o.customer_name,
            "phone_number": o.phone_number,
            "email": o.email,
            "event_type": o.event_type,
            "number_of_guests": o.number_of_guests,
            "event_date": o.event_date,
            "event_time": o.event_time,
            "venue_address": o.venue_address,
            "special_requirements": o.special_requirements,
            "status": o.status,
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "payment_method": o.payment_method,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "items": [{
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price_at_order_time": float(item.price_at_order_time) if item.price_at_order_time else 0,
                "item_name": item.menu_item.item_name if item.menu_item else "Unknown"
            } for item in o.menu_items]
        } for o in orders])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch orders", "details": str(e)}), 500


@orders_bp.route("/", methods=["POST"])
def create_order():
    try:
        data = request.json or {}
        
        # Validate menu_items
        menu_items = data.get("menu_items", [])
        if not menu_items:
            return jsonify({"error": "menu_items is required"}), 400

        # If a JWT is provided, verify it (optional)
        identity = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
        except:
            pass

        # Handle customer_id from JWT - FIX: handle both string and dict
        payload_customer_id = data.get("customer_id")
        identity_customer_id = None
        
        # Extract customer_id based on identity type
        if identity:
            if isinstance(identity, dict):
                identity_customer_id = identity.get("customer_id")
            elif isinstance(identity, (str, int)):
                try:
                    identity_customer_id = int(identity)
                except (ValueError, TypeError):
                    identity_customer_id = None
        
        # Check authorization if both are present
        if payload_customer_id and identity_customer_id:
            if payload_customer_id != identity_customer_id:
                return jsonify({"error": "Forbidden"}), 403
        
        # Use identity customer_id if not provided in payload
        if not payload_customer_id and identity_customer_id:
            data["customer_id"] = identity_customer_id

        # Auto-create or link customer
        customer_id = data.get("customer_id")
        email = data.get("email")
        customer_name = data.get("customer_name")
        phone_number = data.get("phone_number")
        
        new_customer_created = None
        if email and not customer_id:
            existing_customer = Customer.query.filter_by(email=email).first()
            if existing_customer:
                customer_id = existing_customer.customer_id
            else:
                new_customer = Customer(
                    full_name=customer_name or "Guest",
                    email=email,
                    phone_number=phone_number or "",
                    password_hash=None
                )
                db.session.add(new_customer)
                db.session.flush()
                customer_id = new_customer.customer_id
                new_customer_created = new_customer

        # Create order
        order = Order(
            customer_id=customer_id,
            customer_name=customer_name,
            phone_number=phone_number,
            email=email,
            event_type=data.get("event_type"),
            number_of_guests=data.get("guests") or data.get("number_of_guests", 1),
            event_date=data.get("event_date"),
            event_time=data.get("event_time"),
            venue_address=data.get("venue") or data.get("address"),
            special_requirements=data.get("special"),
            total_amount=data.get("total_amount"),
            payment_method=data.get("payment_method", "online")
        )

        db.session.add(order)
        db.session.commit()

        # Save menu items and update stock
        for item in menu_items:
            om = OrderMenuItem(
                order_id=order.order_id,
                menu_item_id=item.get("id"),
                quantity=item.get("qty", 1),
                price_at_order_time=item.get("price", 0)
            )
            db.session.add(om)
            
            # Decrease stock quantity
            menu_item = MenuItem.query.get(item.get("id"))
            if menu_item and menu_item.stock_quantity is not None:
                old_stock = menu_item.stock_quantity
                menu_item.stock_quantity = max(0, menu_item.stock_quantity - item.get("qty", 1))
                
                # Mark as unavailable if stock reaches 0
                if menu_item.stock_quantity == 0:
                    menu_item.is_available = False
                
                # Emit inventory change event
                try:
                    socketio.emit('inventory_changed', {
                        'item_id': menu_item.item_id,
                        'item_name': menu_item.item_name,
                        'old_stock': old_stock,
                        'new_stock': menu_item.stock_quantity,
                        'is_available': menu_item.is_available,
                        'low_stock': menu_item.stock_quantity < 10
                    })
                except Exception as e:
                    pass

        db.session.commit()

        # Update customer order count
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                customer.total_orders_count = Order.query.filter_by(customer_id=customer_id).count()
                db.session.commit()

                # Emit real-time event to admin room for new order
                try:
                    socketio.emit(
                        'order_created',
                        {
                            'order_id': order.order_id,
                            'customer_name': order.customer_name,
                            'phone_number': order.phone_number,
                            'email': order.email,
                            'event_type': order.event_type,
                            'number_of_guests': order.number_of_guests,
                            'event_date': order.event_date,
                            'event_time': order.event_time,
                            'status': order.status,
                            'total_amount': float(order.total_amount) if order.total_amount else 0,
                            'venue_address': order.venue_address,
                            'items': [{
                                'menu_item_id': item.menu_item_id,
                                'quantity': item.quantity,
                                'item_name': item.menu_item.item_name if item.menu_item else "Unknown"
                            } for item in order.menu_items],
                            'created_at': order.created_at.isoformat() if order.created_at else None,
                        },
                        room='admins'
                    )
                except Exception:
                    # Avoid failing the request if socket broadcast fails
                    pass

        return jsonify({"message": "Order Created", "order_id": order.order_id}), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500


@orders_bp.route("/<int:id>", methods=["GET"])
def get_order(id):
    """Get order details by ID - accessible to the customer who placed the order"""
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Optional JWT verification for logged-in customers
        # Non-logged-in customers can still view by order ID (simple security model)
        # For enhanced security in production, require JWT with customer_id match
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                # If JWT is provided, verify customer owns this order
                claims = get_jwt()
                if claims and claims.get("role") != "Admin":
                    customer_id = None
                    if isinstance(identity, dict):
                        customer_id = identity.get("customer_id")
                    elif isinstance(identity, (str, int)):
                        try:
                            customer_id = int(identity)
                        except (ValueError, TypeError):
                            pass
                    
                    if customer_id and order.customer_id != customer_id:
                        return jsonify({"error": "Unauthorized"}), 403
        except:
            # No JWT provided - allow public access (simple model)
            pass

        return jsonify({
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "phone_number": order.phone_number,
            "email": order.email,
            "event_type": order.event_type,
            "number_of_guests": order.number_of_guests,
            "event_date": order.event_date,
            "event_time": order.event_time,
            "venue_address": order.venue_address,
            "special_requirements": order.special_requirements,
            "status": order.status,
            "total_amount": float(order.total_amount) if order.total_amount else 0,
            "payment_method": order.payment_method,
            "razorpay_order_id": order.razorpay_order_id,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "items": [{
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price_at_order_time": float(item.price_at_order_time) if item.price_at_order_time else 0,
                "item_name": item.menu_item.item_name if item.menu_item else "Unknown"
            } for item in order.menu_items]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch order", "details": str(e)}), 500


@orders_bp.route("/status/<int:id>", methods=["PUT"])
@jwt_required()
def update_status(id):
    try:
        claims = get_jwt()
        if not claims or claims.get("role") != "Admin":
            return jsonify({"error": "Forbidden"}), 403
            
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        new_status = request.json.get("status")
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
            
        old_status = order.status
        order.status = new_status
        db.session.commit()
        
        # Emit real-time update to all connected clients
        try:
            socketio.emit(
                'order_status_changed',
                {
                    'order_id': order.order_id,
                    'customer_id': order.customer_id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'customer_name': order.customer_name,
                    'timestamp': order.updated_at.isoformat() if order.updated_at else None
                }
            )
        except Exception as socket_error:
            pass
        
        return jsonify({"message": "Status updated ✔"})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update status", "details": str(e)}), 500
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update status"}), 500