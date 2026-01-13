from flask import Blueprint, request, jsonify, current_app
from extensions import db, socketio, mail
from models import Order, OrderMenuItem, Customer, MenuItem
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from flask_mail import Message
import hashlib
import os
import threading

orders_bp = Blueprint("orders", __name__)

# Track recent order requests to prevent duplicates during network issues
# Key: hash(email + timestamp), Value: order_id
_order_request_cache = {}

def send_order_confirmation_email_async(app, order_data, menu_items_details):
    """Send order confirmation email in background thread"""
    with app.app_context():
        try:
            # Reload order from database in this thread's context
            order = Order.query.get(order_data['order_id'])
            if not order:
                return False
            send_order_confirmation_email(order, menu_items_details)
        except Exception as e:
            print(f"Background email error: {str(e)}")

def send_order_confirmation_email(order, menu_items_details):
    """Send order confirmation email to customer"""
    try:
        # Check if mail is configured
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"⚠️  Email not configured. Order confirmation for {order.email} (Order #{order.order_id})")
            print(f"   Order Details: {order.event_type}, Guests: {order.number_of_guests}, Total: ₹{order.total_amount}")
            return False
        
        # Format items list
        items_html = ""
        for item in menu_items_details:
            items_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{item['name']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: center;">{item['quantity']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: right;">₹{item['price']:.2f}</td>
                </tr>
            """
        
        msg = Message(
            subject=f"Order Confirmation #{order.order_id} - Hotel Shanmuga Bhavaan",
            recipients=[order.email],
            body=f"""
Dear {order.customer_name},

Thank you for choosing Hotel Shanmuga Bhavaan!

Your order has been successfully placed. Here are your order details:

Order #: {order.order_id}
Event Type: {order.event_type}
Number of Guests: {order.number_of_guests}
Event Date: {order.event_date}
Event Time: {order.event_time}
Venue: {order.venue_address}
Total Amount: ₹{order.total_amount:.2f}
Payment Method: {order.payment_method.title()}

Items Ordered:
{chr(10).join([f"- {item['name']} x {item['quantity']} - ₹{item['price']:.2f}" for item in menu_items_details])}

We appreciate your trust in us and look forward to making your event memorable!

Best regards,
Hotel Shanmuga Bhavaan Management Team
            """,
            html=f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 650px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #7a0000, #d4af37); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }}
        .order-box {{ background: #fff8e6; border: 2px solid #d4af37; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .order-details {{ margin: 15px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e6d3a3; }}
        .detail-label {{ font-weight: bold; color: #7a0000; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .items-table th {{ background: #7a0000; color: white; padding: 12px; text-align: left; }}
        .total {{ background: #f5f5f5; font-size: 18px; font-weight: bold; color: #7a0000; padding: 15px; text-align: right; margin-top: 10px; border-radius: 8px; }}
        .thank-you {{ background: linear-gradient(135deg, #fff5e6, #ffe6cc); border-left: 4px solid #d4af37; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Hotel Shanmuga Bhavaan</h1>
            <p style="font-size: 18px; margin: 10px 0 0 0;">Order Confirmation</p>
        </div>
        <div class="content">
            <p>Dear <strong>{order.customer_name}</strong>,</p>
            
            <div class="thank-you">
                <h2 style="color: #7a0000; margin: 0 0 10px 0;">🙏 Thank You for Choosing Our Hotel! 🙏</h2>
                <p style="margin: 0; font-size: 16px;">We are honored to be part of your special event. Your trust means everything to us, and we promise to deliver an unforgettable culinary experience!</p>
            </div>
            
            <div class="order-box">
                <h3 style="color: #7a0000; margin-top: 0;">Order Details</h3>
                <div class="order-details">
                    <div class="detail-row">
                        <span class="detail-label">Order Number:</span>
                        <span>#{order.order_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Event Type:</span>
                        <span>{order.event_type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Number of Guests:</span>
                        <span>{order.number_of_guests}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Event Date:</span>
                        <span>{order.event_date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Event Time:</span>
                        <span>{order.event_time}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Venue:</span>
                        <span>{order.venue_address}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Payment Method:</span>
                        <span>{order.payment_method.title()}</span>
                    </div>
                </div>
            </div>
            
            <h3 style="color: #7a0000;">Items Ordered:</h3>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th style="text-align: center;">Quantity</th>
                        <th style="text-align: right;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="total">
                Total Amount: ₹{order.total_amount:.2f}
            </div>
            
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                We look forward to making your event memorable! If you have any questions or special requests, 
                please don't hesitate to contact us.
            </p>
        </div>
        <div class="footer">
            <p><strong>Hotel Shanmuga Bhavaan Management Team</strong></p>
            <p>© 2026 Hotel Shanmuga Bhavaan. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """
        )
        mail.send(msg)
        print(f"✅ Order confirmation email sent to {order.email} for Order #{order.order_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send order confirmation email: {str(e)}")
        return False

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
        
        # Send immediate response to client
        response = jsonify({"message": "Order Created", "order_id": order.order_id})
        
        # Background tasks: email, socketio, customer stats
        def background_tasks():
            with current_app.app_context():
                try:
                    # Send order confirmation email
                    if order.email:
                        try:
                            send_order_confirmation_email(order, menu_items_details)
                        except Exception as e:
                            print(f"Background email error: {str(e)}")
                    
                    # Emit inventory changes
                    for inv_update in inventory_updates:
                        try:
                            socketio.emit('inventory_changed', inv_update)
                        except Exception as e:
                            pass
                    
                    # Update customer order count
                    if customer_id:
                        try:
                            customer = Customer.query.get(customer_id)
                            if customer:
                                customer.total_orders_count = Order.query.filter_by(customer_id=customer_id).count()
                                db.session.commit()
                        except Exception as e:
                            print(f"Customer stats update error: {str(e)}")
                    
                    # Emit order created event
                    try:
                        socketio.emit(
                            'order_created',
                            {
                                **order_data,
                                'items': [{
                                    'menu_item_id': om.menu_item_id,
                                    'quantity': om.quantity,
                                    'item_name': menu_items_map.get(om.menu_item_id).item_name if menu_items_map.get(om.menu_item_id) else "Unknown"
                                } for om in order_menu_items]
                            },
                            room='admins'
                        )
                    except Exception as e:
                        pass
                except Exception as e:
                    print(f"Background tasks error: {str(e)}")
        
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
        
        return jsonify({"message": "Status updated ✔"})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update status", "details": str(e)}), 500
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to update status"}), 500