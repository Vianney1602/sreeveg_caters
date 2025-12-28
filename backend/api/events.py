from flask import Blueprint, jsonify
from models import EventType

events_bp = Blueprint("events", __name__)

@events_bp.route("/", methods=["GET"])
def get_events():
    events = EventType.query.all()
    return jsonify([{
        "id": e.event_type_id,
        "name": e.event_name,
        "min_guests": e.minimum_guests,
        "description": e.description,
        "image": e.image_url
    } for e in events])
