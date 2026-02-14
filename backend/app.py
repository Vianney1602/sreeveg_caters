import os
import logging

from flask import Flask, jsonify, request
from config import Config
from extensions import db, migrate, socketio
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from logging_config import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup structured logging
    setup_logging(app)
    app.logger.info("Flask application starting", extra={"config": "loaded"})
    
    # JWT configuration
    app.config.setdefault('JWT_SECRET_KEY', os.environ.get('JWT_SECRET_KEY', app.config.get('SECRET_KEY')))

    # Avoid automatic redirects when a trailing slash is missing on routes.
    # This prevents browsers from receiving a 301/302 during CORS preflight OPTIONS requests.
    app.url_map.strict_slashes = False

    db.init_app(app)
    migrate.init_app(app, db)
    # Email is handled by Brevo API (brevo_mail.py) - no Flask extension needed
    # initialize JWT manager
    jwt = JWTManager()
    jwt.init_app(app)
    # Enable CORS so the React frontend can call the API.
    # In production, set CORS_ALLOWED_ORIGINS in .env to your domains.
    allowed = Config.parse_origins(app.config.get("CORS_ALLOWED_ORIGINS"))
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                ],
                "supports_credentials": True,
            },
            r"/static/*": {
                "origins": allowed,
                "methods": ["GET", "OPTIONS"],
                "allow_headers": ["Content-Type"],
            }
        },
    )

    # Initialize SocketIO with CORS settings and production-ready config
    socketio.init_app(
        app,
        cors_allowed_origins=allowed,
        async_mode="threading",
        allow_upgrades=False,  # force long-polling to avoid websocket issues
        # Production-ready session settings
        ping_timeout=60,
        ping_interval=25,
        engineio_logger=False,
        manage_session=False,  # Don't manage sessions to avoid encoding issues
    )

    # Import models
    from models import (
        Customer, Order, MenuItem, EventType,
        OrderMenuItem, MonthlyStat, ContactInquiry, UploadedImage
    )

    # Register API Blueprints
    from api.customers import customers_bp
    from api.orders import orders_bp
    from api.menu import menu_bp
    from api.events import events_bp
    from api.stats import stats_bp
    from api.admin import admin_bp
    from api.payments import payments_bp
    from api.uploads import uploads_bp
    from api.users import users_bp

    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(menu_bp, url_prefix="/api/menu")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Compatibility aliases: expose common POST login/register endpoints
    # so clients that expect app-level routes still work.
    try:
        from api.customers import register_customer, login_customer

        app.add_url_rule('/api/customers/register', 'register_customer_alias', register_customer, methods=['POST'])
        app.add_url_rule('/api/customers/login', 'login_customer_alias', login_customer, methods=['POST'])
    except Exception:
        # If import fails for any reason, continue silently; blueprints still registered.
        pass


    @app.route("/")
    def home():
        return {"message": "Flask Backend Running ✔"}
    
    # Serve static files (uploaded images)
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        from flask import send_from_directory
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        return send_from_directory(static_dir, filename)

    @app.route("/health", methods=["GET"]) 
    def health():
        try:
            # simple DB check
            from models import Customer
            Customer.query.limit(1).all()
            app.logger.info("Health check passed")
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return jsonify({"status": "error", "message": "Database connection failed"}), 500

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f"Bad request: {str(e)}")
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"error": "File too large", "message": "Uploaded file exceeds size limit"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

    # Compatibility endpoints expected by the React frontend
    @app.route('/api/event_types', methods=['GET'])
    def event_types_alias():
        events = EventType.query.all()
        return jsonify([{
            'event_type_id': e.event_type_id,
            'event_name': e.event_name,
            'minimum_guests': e.minimum_guests,
            'description': e.description,
            'image_url': e.image_url
        } for e in events])

    @app.route('/api/menu_items', methods=['GET'])
    def menu_items_alias():
        # Expose only available items for customer-facing menus
        items = MenuItem.query.filter_by(is_available=True).all()
        return jsonify([{
            'item_id': m.item_id,
            'item_name': m.item_name,
            'category': m.category,
            'price_per_plate': m.price_per_plate,
            'is_vegetarian': m.is_vegetarian,
            'image_url': m.image_url,
            'description': m.description,
            'is_available': m.is_available,
            'stock_quantity': m.stock_quantity if m.stock_quantity is not None else 100
        } for m in items])

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection with JWT authentication"""
        try:
            from flask_socketio import disconnect
            from flask import request
            import jwt as pyjwt
            
            # Get token from auth dict or connection args
            token = auth.get('token') if auth else None
            
            if token:
                try:
                    # Verify the JWT token
                    secret_key = app.config.get('JWT_SECRET_KEY')
                    decoded = pyjwt.decode(token, secret_key, algorithms=['HS256'])
                    
                    # Get user identity from token
                    identity = decoded.get('sub')  # 'sub' is the standard JWT claim for identity
                    
                    # Store user info in the session for this socket
                    request.sid_data = {
                        'identity': identity,
                        'authenticated': True,
                        'role': decoded.get('role')
                    }
                    
                    # Join user-specific room for targeted messaging
                    from flask_socketio import join_room
                    if isinstance(identity, dict):
                        user_id = identity.get('customer_id') or identity.get('admin_id')
                        if user_id:
                            room = f"user_{user_id}"
                            join_room(room)

                    # Admins also join the shared admin room for dashboards
                    if decoded.get('role') == 'Admin':
                        join_room('admins')
                    
                    return {'status': 'connected', 'authenticated': True}
                    
                except pyjwt.ExpiredSignatureError:
                    disconnect()
                    return {'status': 'error', 'message': 'Token expired'}
                    
                except pyjwt.InvalidTokenError as e:
                    disconnect()
                    return {'status': 'error', 'message': 'Invalid token'}
            else:
                # Allow unauthenticated connections but mark them as such
                request.sid_data = {'authenticated': False}
                return {'status': 'connected', 'authenticated': False}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        pass

    @socketio.on('join')
    def handle_join(data):
        """Allow clients to join specific rooms for targeted messaging"""
        room = data.get('room')
        if room:
            from flask_socketio import join_room
            join_room(room)

    @socketio.on('leave')
    def handle_leave(data):
        """Allow clients to leave rooms"""
        room = data.get('room')
        if room:
            from flask_socketio import leave_room
            leave_room(room)

    return app

app = create_app()

if __name__ == "__main__":
    # If SSL cert + key exist in the backend folder (cert.pem/key.pem), run HTTPS for local dev.
    base = os.path.dirname(__file__)
    cert = os.path.join(base, 'cert.pem')
    key = os.path.join(base, 'key.pem')
    if os.path.exists(cert) and os.path.exists(key):
        socketio.run(app, host="0.0.0.0", port=5000, debug=False, ssl_context=(cert, key))
    else:
        socketio.run(app, host="0.0.0.0", port=5000, debug=False)
