from flask import Blueprint, request, jsonify
import os
from extensions import db, socketio
from models import MenuItem, UploadedImage
def _delete_image_asset(image_url: str):
    """Remove stored image from disk or database based on URL."""
    if not image_url:
        return

    # Legacy disk-based uploads
    if image_url.startswith('/static/uploads/'):
        try:
            filename = image_url.split('/static/uploads/')[-1]
            base = os.path.dirname(os.path.abspath(__file__))
            root = os.path.abspath(os.path.join(base, ".."))
            file_path = os.path.join(root, "static", "uploads", filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting old image: {e}")
        return

    # Database-backed uploads
    if '/api/uploads/image/' in image_url:
        try:
            image_id_str = image_url.rstrip('/').split('/')[-1]
            image_id = int(image_id_str)
            image = UploadedImage.query.get(image_id)
            if image:
                db.session.delete(image)
        except Exception as e:
            print(f"Error deleting stored image {image_url}: {e}")

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
    categories = data.get("categories", [data.get("category")])
    if isinstance(categories, str):
        categories = [categories]
    
    item = MenuItem(
        item_name=data["item_name"],
        category=categories,  # Store as JSON array
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
    })
    
    return jsonify({"message": "Item Added", "item_id": item.item_id})

@menu_bp.route("/<int:id>", methods=["PUT"])
def update_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    data = request.json
    
    # If new image is provided and different from old, delete old image
    new_image_url = data.get("image")
    if new_image_url and new_image_url != item.image_url:
        _delete_image_asset(item.image_url)
    
    item.item_name = data.get("item_name", item.item_name)
    
    # Handle categories - support both single and multiple
    if "categories" in data:
        categories = data["categories"]
        if isinstance(categories, str):
            categories = [categories]
        item.category = categories
    elif "category" in data:
        category = data["category"]
        if isinstance(category, str):
            item.category = [category]
        else:
            item.category = category
    
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
    })
    
    return jsonify({"message": "Item Updated"})

@menu_bp.route("/<int:id>", methods=["DELETE"])
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    item_id = item.item_id
    old_image_url = item.image_url
    
    # Delete the item from database and associated stored image
    _delete_image_asset(old_image_url)
    db.session.delete(item)
    db.session.commit()
    
    # Broadcast item deletion to all clients
    socketio.emit('menu_item_deleted', {
        'item_id': item_id
    })
    
    return jsonify({"message": "Item Deleted"})
