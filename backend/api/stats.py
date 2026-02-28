from flask import Blueprint, jsonify
from extensions import db
from models import Order, MenuItem
from sqlalchemy import func

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/summary", methods=["GET"])
def get_stats():
    from sqlalchemy import case, func
    stats = db.session.query(
        func.count(Order.order_id).label('total_orders'),
        func.sum(Order.total_amount).label('revenue'),
        func.sum(case((Order.status == 'Confirmed', 1), else_=0)).label('confirmed_orders'),
        func.sum(case((Order.status == 'Pending', 1), else_=0)).label('pending_orders'),
    ).first()

    total_orders = stats.total_orders or 0
    revenue = stats.revenue or 0
    confirmed = stats.confirmed_orders or 0
    pending = stats.pending_orders or 0

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
