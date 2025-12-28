from flask import Blueprint, request, jsonify
import os
from extensions import db, socketio
from models import MenuItem

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("/", methods=["GET"])
def get_menu():
    items = MenuItem.query.all()
    return jsonify([{
        "item_id": m.item_id,
        "item_name": m.item_name,
        "price_per_plate": m.price_per_plate,
        "category": m.category,
        "is_vegetarian": m.is_vegetarian,
        "image_url": m.image_url,
        "description": m.description,
        "is_available": m.is_available,
        "stock_quantity": m.stock_quantity if m.stock_quantity is not None else 100
    } for m in items])

@menu_bp.route("/", methods=["POST"])
def add_menu_item():
    data = request.json
    item = MenuItem(
        item_name=data["item_name"],
        category=data["category"],
        price_per_plate=data["price"],
        is_vegetarian=data.get("veg", True),
        image_url=data.get("image"),
        description=data.get("description")
    )
    db.session.add(item)
    db.session.commit()
    
    # Broadcast new menu item to all clients
    socketio.emit('menu_item_added', {
        'item_id': item.item_id,
        'item_name': item.item_name,
        'price_per_plate': float(item.price_per_plate),
        'category': item.category,
        'is_vegetarian': item.is_vegetarian,
        'image_url': item.image_url,
        'description': item.description,
        'is_available': item.is_available,
        'stock_quantity': item.stock_quantity if item.stock_quantity is not None else 100
    }, broadcast=True)
    
    return jsonify({"message": "Item Added", "item_id": item.item_id})

@menu_bp.route("/<int:id>", methods=["PUT"])
def update_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    data = request.json
    
    # If new image is provided and different from old, delete old image
    new_image_url = data.get("image")
    if new_image_url and new_image_url != item.image_url:
        old_image_url = item.image_url
        if old_image_url and old_image_url.startswith('/static/uploads/'):
            try:
                filename = old_image_url.split('/static/uploads/')[-1]
                base = os.path.dirname(os.path.abspath(__file__))
                root = os.path.abspath(os.path.join(base, ".."))
                file_path = os.path.join(root, "static", "uploads", filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting old image: {e}")
    
    item.item_name = data.get("item_name", item.item_name)
    item.category = data.get("category", item.category)
    item.price_per_plate = data.get("price", item.price_per_plate)
    item.is_vegetarian = data.get("veg", item.is_vegetarian)
    item.image_url = data.get("image", item.image_url)
    item.description = data.get("description", item.description)
    item.is_available = data.get("is_available", item.is_available)
    db.session.commit()
    
    # Broadcast updated menu item to all clients
    socketio.emit('menu_item_updated', {
        'item_id': item.item_id,
        'item_name': item.item_name,
        'price_per_plate': float(item.price_per_plate),
        'category': item.category,
        'is_vegetarian': item.is_vegetarian,
        'image_url': item.image_url,
        'description': item.description,
        'is_available': item.is_available,
        'stock_quantity': item.stock_quantity if item.stock_quantity is not None else 100
    }, broadcast=True)
    
    return jsonify({"message": "Item Updated"})

@menu_bp.route("/<int:id>", methods=["DELETE"])
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    item_id = item.item_id
    old_image_url = item.image_url
    
    # Delete the item from database
    db.session.delete(item)
    db.session.commit()
    
    # Delete associated image file if it exists
    if old_image_url and old_image_url.startswith('/static/uploads/'):
        try:
            # Extract filename from URL
            filename = old_image_url.split('/static/uploads/')[-1]
            # Construct absolute path to the image file
            base = os.path.dirname(os.path.abspath(__file__))  # .../backend/api
            root = os.path.abspath(os.path.join(base, ".."))  # .../backend
            file_path = os.path.join(root, "static", "uploads", filename)
            
            # Remove file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Log error but don't fail the deletion
            print(f"Error deleting image file: {e}")
    
    # Broadcast item deletion to all clients
    socketio.emit('menu_item_deleted', {
        'item_id': item_id
    }, broadcast=True)
    
    return jsonify({"message": "Item Deleted"})
