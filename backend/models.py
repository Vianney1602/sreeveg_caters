from datetime import datetime
from extensions import db


class UploadedImage(db.Model):
    __tablename__ = "uploaded_images"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(64), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 1. CUSTOMERS TABLE
class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_orders_count = db.Column(db.Integer, default=0)

    orders = db.relationship("Order", backref="customer", lazy=True)


# 2. ORDERS TABLE
class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"))
    customer_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))

    event_type = db.Column(db.String(50))
    number_of_guests = db.Column(db.Integer)
    event_date = db.Column(db.String(20))
    event_time = db.Column(db.String(20))
    venue_address = db.Column(db.Text)
    special_requirements = db.Column(db.Text)

    status = db.Column(db.String(20), default="Out for Delivery")
    total_amount = db.Column(db.Float, default=0.0)
    razorpay_order_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(20), default="online")  # 'online' or 'cod'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    menu_items = db.relationship("OrderMenuItem", backref="order", lazy=True)


# 3. MENU_ITEMS TABLE
class MenuItem(db.Model):
    __tablename__ = "menu_items"

    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.JSON)  # Changed to JSON to support multiple categories
    price_per_plate = db.Column(db.Float)
    is_vegetarian = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))
    description = db.Column(db.String(255))
    total_orders_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=100)  # Track available stock
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderMenuItem", backref="menu_item", lazy=True)


# 4. ORDER_MENU_ITEMS TABLE (Many-to-Many)
class OrderMenuItem(db.Model):
    __tablename__ = "order_menu_items"

    order_menu_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.item_id"))

    quantity = db.Column(db.Integer, default=1)
    price_at_order_time = db.Column(db.Float)


# 5. EVENT_TYPES TABLE
class EventType(db.Model):
    __tablename__ = "event_types"

    event_type_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(50))
    minimum_guests = db.Column(db.Integer)
    description = db.Column(db.String(255))
    icon_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)


# 6. MONTHLY STATISTICS
class MonthlyStat(db.Model):
    __tablename__ = "monthly_statistics"

    stat_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    total_orders = db.Column(db.Integer)
    total_revenue = db.Column(db.Float)
    confirmed_orders = db.Column(db.Integer)
    pending_orders = db.Column(db.Integer)
    completed_orders = db.Column(db.Integer)
    cancelled_orders = db.Column(db.Integer)


# 7. CONTACT INQUIRIES
class ContactInquiry(db.Model):
    __tablename__ = "contact_inquiries"

    inquiry_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)
    inquiry_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="New")


# Admin model removed - admin authentication now uses hardcoded credentials for website owner only
