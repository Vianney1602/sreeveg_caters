from flask import Blueprint, request, jsonify
import os
import re
from extensions import db, socketio
from models import MenuItem, UploadedImage

# Optional AWS S3 import
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# S3 client lazy loading
_s3_client = None

def get_s3_client():
    """Get or create S3 client."""
    global _s3_client
    if not BOTO3_AVAILABLE:
        return None
    if _s3_client is None:
        from config import Config
        if Config.AWS_S3_ENABLED:
            _s3_client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_S3_REGION
            )
    return _s3_client

def _delete_image_asset(image_url: str):
    """Remove stored image from S3 or database based on URL."""
    if not image_url:
        return

    # S3 URL deletion
    if 's3' in image_url and '.amazonaws.com' in image_url:
        try:
            from config import Config
            from urllib.parse import unquote_plus
            # Extract bucket name and key from S3 URL
            # Virtual-hosted: https://bucket.name.s3.region.amazonaws.com/key
            # Path-style:     https://s3.region.amazonaws.com/bucket.name/key
            match = re.search(r'https://(.+)\.s3\.[^.]+\.amazonaws\.com/(.+)', image_url)
            if not match:
                # Try path-style URL format
                match = re.search(r'https://s3\.[^.]+\.amazonaws\.com/([^/]+)/(.+)', image_url)
            if match:
                bucket_name = match.group(1)
                key = unquote_plus(match.group(2))  # Decode URL-encoded key (+ -> space)
                
                s3_client = get_s3_client()
                if s3_client:
                    s3_client.delete_object(Bucket=bucket_name, Key=key)
                    print(f"✓ Deleted S3 object: {key}")
        except ClientError as e:
            print(f"Error deleting S3 object: {e}")
        except Exception as e:
            print(f"Error deleting S3 image {image_url}: {e}")
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
                print(f"✓ Deleted local file: {file_path}")
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
                print(f"✓ Deleted database image: {image_id}")
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
