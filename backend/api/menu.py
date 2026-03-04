from flask import Blueprint, request, jsonify
import os
import re
import base64
import uuid
from extensions import db, socketio, emit_with_namespace
from models import MenuItem, UploadedImage

# S3 client lazy loading
_s3_client = None

def get_s3_client():
    """Get or create S3 client with real lazy load logic."""
    global _s3_client
    if _s3_client is None:
        try:
            import boto3
            from config import Config
            if Config.AWS_S3_ENABLED:
                _s3_client = boto3.client(
                    's3',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_S3_REGION
                )
        except ImportError:
            pass
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
        except Exception as e:
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

import threading

def _delete_image_asset_background(image_url: str):
    """Run `_delete_image_asset` in a background thread with app context."""
    if not image_url:
        return
        
    from flask import current_app
    app = current_app._get_current_object()
    
    def _run_with_context(url):
        with app.app_context():
            try:
                _delete_image_asset(url)
                # Ensure we commit if a database image was deleted
                if '/api/uploads/image/' in url:
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error in background image deletion: {e}")
                
    thread = threading.Thread(target=_run_with_context, args=(image_url,), daemon=True)
    thread.start()


def _handle_base64_image(image_value):
    """If image_value is a base64 data URL, decode and upload to S3.
    Returns the S3 URL on success, or the original value if not base64."""
    if not image_value or not isinstance(image_value, str):
        return image_value
    if not image_value.startswith('data:image/'):
        return image_value

    try:
        # Parse data URL: data:image/jpeg;base64,/9j/4AAQ...
        header, b64data = image_value.split(',', 1)
        # Extract mime type
        mime_type = header.split(':')[1].split(';')[0]  # e.g. image/jpeg
        ext_map = {
            'image/jpeg': '.jpg', 'image/png': '.png',
            'image/webp': '.webp', 'image/gif': '.gif',
        }
        ext = ext_map.get(mime_type, '.jpg')
        file_bytes = base64.b64decode(b64data)
        filename = f"menu_item_{uuid.uuid4().hex[:10]}{ext}"

        # Import upload_to_s3 from uploads module
        from api.uploads import upload_to_s3
        s3_url = upload_to_s3(file_bytes, filename, mime_type)
        if s3_url:
            print(f"[OK] Base64 image uploaded to S3: {s3_url}")
            return s3_url
        else:
            print("[WARN] S3 upload returned None, keeping data URL trimmed")
            return ''  # Don't store huge base64 in DB
    except Exception as e:
        print(f"[WARN] Base64 image processing failed: {e}")
        return ''


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
    
    # Handle base64 image inline upload
    image_url = _handle_base64_image(data.get("image"))
    
    item = MenuItem(
        item_name=data["item_name"],
        category=categories,  # Store as JSON array
        price_per_plate=data["price"],
        is_vegetarian=data.get("veg", True),
        image_url=image_url,
        description=data.get("description")
    )
    db.session.add(item)
    db.session.commit()
    
    # Broadcast new menu item to all clients
    socketio.start_background_task(emit_with_namespace, 'menu_item_added', {
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
    
    # Handle base64 image inline upload
    new_image_url = _handle_base64_image(data.get("image"))
    
    # If new image is provided and different from old, delete old image in background
    if new_image_url and new_image_url != item.image_url:
        _delete_image_asset_background(item.image_url)
    
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
    item.image_url = new_image_url if new_image_url else item.image_url
    item.description = data.get("description", item.description)
    item.is_available = data.get("is_available", item.is_available)
    # Get the ID before the background thread
    item_id = item.item_id
    item_name = item.item_name
    price_per_plate = float(item.price_per_plate)
    category = item.category
    is_vegetarian = item.is_vegetarian
    image_url = item.image_url
    description = item.description
    is_available = item.is_available
    stock_quantity = item.stock_quantity if item.stock_quantity is not None else 100

    import time
    t0 = time.time()
    db.session.commit()
    t1 = time.time()
    print(f"DB COMMIT TIME: {t1-t0:.3f}s")
    
    # Broadcast updated menu item to all clients in background thread
    socketio.start_background_task(emit_with_namespace, 'menu_item_updated', {
        'item_id': item_id,
        'item_name': item_name,
        'price_per_plate': price_per_plate,
        'category': category,
        'is_vegetarian': is_vegetarian,
        'image_url': image_url,
        'description': description,
        'is_available': is_available,
        'stock_quantity': stock_quantity
    })
    
    return jsonify({"message": "Item Updated"})

@menu_bp.route("/<int:id>", methods=["DELETE"])
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    item_id = item.item_id
    old_image_url = item.image_url
    
    # Delete the item from database and associated stored image in background
    _delete_image_asset_background(old_image_url)
    db.session.delete(item)
    db.session.commit()
    
    # Broadcast item deletion to all clients in background thread
    socketio.start_background_task(emit_with_namespace, 'menu_item_deleted', {
        'item_id': item_id
    })
    
    return jsonify({"message": "Item Deleted"})
