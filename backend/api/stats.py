from flask import Blueprint, jsonify
from extensions import db
from models import Order, MenuItem
from sqlalchemy import func

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/summary", methods=["GET"])
def get_stats():
    total_orders = Order.query.count()
    revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0

    confirmed = Order.query.filter_by(status="Confirmed").count()
    pending = Order.query.filter_by(status="Pending").count()

    top_dishes = MenuItem.query.order_by(MenuItem.total_orders_count.desc()).limit(5).all()

    return jsonify({
        "total_orders": total_orders,
        "revenue": revenue,
        "confirmed": confirmed,
        "pending": pending,
        "top_dishes": [
            {"name": d.item_name, "orders": d.total_orders_count}
            for d in top_dishes
        ]
    })
