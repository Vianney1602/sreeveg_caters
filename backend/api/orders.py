from flask import Blueprint, request, jsonify, current_app
from extensions import db, socketio
from models import Order, OrderMenuItem, Customer, MenuItem
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from brevo_mail import send_order_confirmation_email, send_order_cancellation_email
import hashlib
import os
import threading

orders_bp = Blueprint("orders", __name__)

# Track recent order requests to prevent duplicates during network issues
# Key: hash(email + timestamp), Value: order_id
_order_request_cache = {}

def emit_stats_update():
    """Emit updated stats to all admin clients"""
    try:
        total_orders = Order.query.count()
        revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        confirmed = Order.query.filter_by(status="Confirmed").count()
        pending = Order.query.filter_by(status="Pending").count()
        delivered = Order.query.filter_by(status="Delivered").count()
        cancelled = Order.query.filter_by(status="Cancelled").count()
        
        socketio.emit(
            'stats_updated',
            {
                'total_orders': total_orders,
                'revenue': float(revenue),
                'confirmed': confirmed,
                'pending': pending,
                'delivered': delivered,
                'cancelled': cancelled
            },
            room='admins'
        )
    except Exception as e:
        print(f"Failed to emit stats update: {str(e)}")

def send_order_confirmation_email_async(app, order_data, menu_items_details):
    """Send order confirmation email in background thread using Brevo"""
    with app.app_context():
        try:
            order = Order.query.get(order_data['order_id'])
            if not order:
                return False
            send_order_confirmation_email(order, menu_items_details)
        except Exception as e:
            print(f"Background email error: {str(e)}")

def send_order_cancellation_email_async(app, order_id):
    """Send order cancellation email in background thread using Brevo"""
    with app.app_context():
        try:
            order = Order.query.get(order_id)
            if not order:
                return False
            send_order_cancellation_email(order)
        except Exception as e:
            print(f"Background cancellation email error: {str(e)}")

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

        # Duplicate detection: Check if same email created order in last 5 seconds
        email = data.get("email", "").lower().strip()
        if email:
            current_time = datetime.utcnow()
            request_hash = hashlib.md5(email.encode()).hexdigest()
            
            # Check cache for recent requests from same email
            if request_hash in _order_request_cache:
                cached_time, cached_order_id = _order_request_cache[request_hash]
                time_diff = (current_time - cached_time).total_seconds()
                
                # If within 5 seconds, return cached order (likely duplicate submission)
                if time_diff < 5:
                    return jsonify({
                        "message": "Order already exists",
                        "order_id": cached_order_id,
                        "duplicate": True
                    }), 201
            
            # Clean old entries (older than 10 seconds)
            _order_request_cache.clear() if len(_order_request_cache) > 100 else None


        # If a JWT is provided, verify it (optional)
        identity = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
        except:
            pass
        
        # Also check for user token from our new auth system
        user_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_customer_id = None
        if user_token and not identity:
            try:
                import jwt
                SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
                decoded = jwt.decode(user_token, SECRET_KEY, algorithms=["HS256"])
                user_customer_id = decoded.get('user_id')
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
        
        # Use user_customer_id if available
        if user_customer_id and not identity_customer_id:
            identity_customer_id = user_customer_id
        
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
        db.session.flush()  # Get order_id without full commit
        
        # Cache this order to prevent duplicates from rapid submissions
        if email:
            request_hash = hashlib.md5(email.encode()).hexdigest()
            _order_request_cache[request_hash] = (datetime.utcnow(), order.order_id)

        # Bulk load all menu items to avoid N+1 queries
        menu_item_ids = [item.get("id") for item in menu_items]
        menu_items_map = {mi.item_id: mi for mi in MenuItem.query.filter(MenuItem.item_id.in_(menu_item_ids)).all()}
        
        # Prepare batch operations
        order_menu_items = []
        inventory_updates = []
        
        # Save menu items and prepare stock updates
        for item in menu_items:
            om = OrderMenuItem(
                order_id=order.order_id,
                menu_item_id=item.get("id"),
                quantity=item.get("qty", 1),
                price_at_order_time=item.get("price", 0)
            )
            db.session.add(om)
            order_menu_items.append(om)
            
            # Decrease stock quantity
            menu_item = menu_items_map.get(item.get("id"))
            if menu_item and menu_item.stock_quantity is not None:
                old_stock = menu_item.stock_quantity
                menu_item.stock_quantity = max(0, menu_item.stock_quantity - item.get("qty", 1))
                
                # Mark as unavailable if stock reaches 0
                if menu_item.stock_quantity == 0:
                    menu_item.is_available = False
                
                inventory_updates.append({
                    'item_id': menu_item.item_id,
                    'item_name': menu_item.item_name,
                    'old_stock': old_stock,
                    'new_stock': menu_item.stock_quantity,
                    'is_available': menu_item.is_available,
                    'low_stock': menu_item.stock_quantity < 10
                })

        # Single commit for all database operations
        db.session.commit()
        
        # Prepare data for background tasks
        order_data = {
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
            'created_at': order.created_at.isoformat() if order.created_at else None,
        }
        
        # Prepare menu items details for email
        menu_items_details = []
        for om in order_menu_items:
            menu_item = menu_items_map.get(om.menu_item_id)
            menu_items_details.append({
                'name': menu_item.item_name if menu_item else 'Unknown Item',
                'quantity': om.quantity,
                'price': float(om.price_at_order_time)
            })
        
        # IMMEDIATE: Emit order_created event to admin dashboard (don't wait for background thread)
        try:
            order_payload = {
                **order_data,
                'items': [{
                    'menu_item_id': om.menu_item_id,
                    'quantity': om.quantity,
                    'item_name': menu_items_map.get(om.menu_item_id).item_name if menu_items_map.get(om.menu_item_id) else "Unknown"
                } for om in order_menu_items]
            }
            socketio.emit('order_created', order_payload, room='admins')
            print(f"✅ Emitted order_created event for Order #{order.order_id} to admins room")
        except Exception as e:
            print(f"❌ Failed to emit order_created: {str(e)}")
        
        # IMMEDIATE: Emit stats update
        try:
            emit_stats_update()
            print(f"✅ Emitted stats_updated event to admins room")
        except Exception as e:
            print(f"❌ Failed to emit stats_updated: {str(e)}")
        
        # Send immediate response to client
        response = jsonify({"message": "Order Created", "order_id": order.order_id})
        
        # Capture the real app object for background thread (current_app proxy doesn't work in threads)
        app = current_app._get_current_object()
        # Save order ID and email for thread safety (ORM objects may detach from session)
        _order_id = order.order_id
        _order_email = order.email
        _customer_id = customer_id
        
        # Send order confirmation email IMMEDIATELY (not in background thread)
        # Background threads can silently fail under gunicorn/eventlet
        if _order_email:
            try:
                fresh_order = Order.query.get(_order_id)
                if fresh_order:
                    email_result = send_order_confirmation_email(fresh_order, menu_items_details)
                    if email_result:
                        print(f"✅ Order confirmation email sent for Order #{_order_id} to {_order_email}")
                    else:
                        print(f"⚠️ Order confirmation email failed for Order #{_order_id}")
                else:
                    print(f"❌ Could not find Order #{_order_id} for email")
            except Exception as e:
                print(f"❌ Email error for Order #{_order_id}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Background tasks: inventory updates, customer stats (non-critical)
        def background_tasks():
            with app.app_context():
                try:
                    # Emit inventory changes
                    for inv_update in inventory_updates:
                        try:
                            socketio.emit('inventory_changed', inv_update)
                        except Exception as e:
                            pass
                    
                    # Update customer order count
                    if _customer_id:
                        try:
                            customer = Customer.query.get(_customer_id)
                            if customer:
                                customer.total_orders_count = Order.query.filter_by(customer_id=_customer_id).count()
                                db.session.commit()
                        except Exception as e:
                            print(f"Customer stats update error: {str(e)}")
                except Exception as e:
                    print(f"❌ Background tasks error: {str(e)}")
        
        # Start background thread
        thread = threading.Thread(target=background_tasks)
        thread.daemon = True
        thread.start()

        return response, 201
        
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


@orders_bp.route("/<int:id>/request-cancel", methods=["POST"])
def request_cancel_order(id):
    """Customer requests order cancellation"""
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check if order is already delivered or cancelled
        if order.status.lower() in ['delivered', 'cancelled']:
            return jsonify({"error": f"Cannot cancel order that is already {order.status.lower()}"}), 400
        
        # Verify customer ownership (check token if available)
        user_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if user_token:
            try:
                import jwt as pyjwt
                SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
                decoded = pyjwt.decode(user_token, SECRET_KEY, algorithms=["HS256"])
                user_customer_id = decoded.get('user_id')
                if order.customer_id and user_customer_id != order.customer_id:
                    return jsonify({"error": "Unauthorized"}), 403
            except:
                pass
        
        # Mark as cancellation requested
        order.special_requirements = (order.special_requirements or '') + f"\n[CANCELLATION REQUESTED at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}]"
        db.session.commit()
        
        # Emit socket event to admin
        try:
            socketio.emit(
                'cancellation_requested',
                {
                    'order_id': order.order_id,
                    'customer_name': order.customer_name,
                    'customer_id': order.customer_id,
                    'email': order.email,
                    'phone_number': order.phone_number,
                    'event_type': order.event_type,
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'status': order.status,
                    'requested_at': datetime.utcnow().isoformat()
                },
                room='admins'
            )
        except Exception as e:
            print(f"Failed to emit cancellation request: {str(e)}")
        
        return jsonify({"message": "Cancellation request sent to admin for approval"}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to request cancellation", "details": str(e)}), 500


@orders_bp.route("/<int:id>/approve-cancel", methods=["POST"])
@jwt_required()
def approve_cancel_order(id):
    """Admin approves order cancellation"""
    try:
        claims = get_jwt()
        if not claims or claims.get("role") != "Admin":
            return jsonify({"error": "Forbidden - Admin only"}), 403
        
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check if order is already delivered
        if order.status.lower() == 'delivered':
            return jsonify({"error": "Cannot cancel delivered order"}), 400
        
        data = request.json or {}
        approved = data.get('approved', True)
        
        if approved:
            old_status = order.status
            order.status = "Cancelled"
            db.session.commit()
            
            # Restore stock for cancelled order
            for item in order.menu_items:
                menu_item = MenuItem.query.get(item.menu_item_id)
                if menu_item and menu_item.stock_quantity is not None:
                    menu_item.stock_quantity += item.quantity
                    if menu_item.stock_quantity > 0:
                        menu_item.is_available = True
            
            db.session.commit()
            
            # Emit real-time update to all clients
            try:
                socketio.emit(
                    'order_status_changed',
                    {
                        'order_id': order.order_id,
                        'customer_id': order.customer_id,
                        'old_status': old_status,
                        'new_status': 'Cancelled',
                        'customer_name': order.customer_name,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                
                # Also emit cancellation approved event
                socketio.emit(
                    'cancellation_approved',
                    {
                        'order_id': order.order_id,
                        'customer_id': order.customer_id,
                        'status': 'Cancelled'
                    }
                )
            except Exception as e:
                print(f"Failed to emit cancellation approval: {str(e)}")
            
            # Send cancellation email to customer IMMEDIATELY
            if order.email:
                try:
                    email_result = send_order_cancellation_email(order)
                    if email_result:
                        print(f"✅ Cancellation email sent for Order #{order.order_id} to {order.email}")
                    else:
                        print(f"⚠️ Cancellation email failed for Order #{order.order_id}")
                except Exception as e:
                    print(f"Failed to send cancellation email: {str(e)}")
            
            return jsonify({"message": "Order cancelled successfully"}), 200
        else:
            # Admin rejected cancellation - just notify
            try:
                socketio.emit(
                    'cancellation_rejected',
                    {
                        'order_id': order.order_id,
                        'customer_id': order.customer_id,
                    }
                )
            except Exception as e:
                print(f"Failed to emit cancellation rejection: {str(e)}")
            
            return jsonify({"message": "Cancellation request rejected"}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to process cancellation", "details": str(e)}), 500


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

        # If status moved to Paid, ensure customer segment gets the new customer immediately
        if new_status == "Paid" and order.customer_id:
            try:
                customer = Customer.query.get(order.customer_id)
                if customer:
                    orders_for_customer = Order.query.filter_by(customer_id=order.customer_id).all()
                    total_spent = sum((o.total_amount or 0) for o in orders_for_customer)
                    orders_count = len(orders_for_customer)

                    customer.total_orders_count = orders_count
                    db.session.commit()

                    payload = {
                        "customer_id": customer.customer_id,
                        "full_name": customer.full_name,
                        "phone_number": customer.phone_number,
                        "email": customer.email,
                        "total_orders_count": orders_count,
                        "total_spent": float(total_spent),
                        "created_at": customer.created_at.isoformat() if customer.created_at else None,
                        "is_registered": bool(customer.password_hash),
                    }
                    socketio.emit('customer_created', payload, room='admins')
            except Exception:
                pass
        
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
        
        # Emit stats update after status change
        try:
            emit_stats_update()
        except Exception:
            pass
        
        return jsonify({"message": "Status updated ✔"})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update status", "details": str(e)}), 500