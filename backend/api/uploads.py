from flask import Blueprint, request, jsonify, current_app, send_file
from io import BytesIO
import os
import uuid
from werkzeug.utils import secure_filename
from extensions import db
from models import UploadedImage

# Optional AWS S3 import
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

uploads_bp = Blueprint("uploads", __name__)

# Initialize S3 client lazily
_s3_client = None

def get_s3_client():
    """Get or create S3 client if AWS is configured."""
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

def _allowed_extensions():
    exts = current_app.config.get("ALLOWED_IMAGE_EXTENSIONS")
    if isinstance(exts, (set, list, tuple)):
        return set(map(str.lower, exts))
    if isinstance(exts, str):
        return set(x.strip().lower() for x in exts.split(",") if x.strip())
    return {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _allowed_extensions()


def upload_to_s3(file_bytes, filename, mime_type):
    """Upload file to AWS S3 and return the public URL."""
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
        
        from config import Config
        bucket_name = Config.AWS_S3_BUCKET_NAME
        
        # Generate unique key to avoid filename collisions
        # Format: menu items/originalname.ext (matches existing S3 structure)
        file_name_clean = secure_filename(filename)
        name, ext = os.path.splitext(file_name_clean)
        # Use 'menu items/' prefix to match existing bucket structure
        unique_filename = f"menu items/{name}{ext}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=unique_filename,
            Body=file_bytes,
            ContentType=mime_type,
            ACL='public-read'  # Make file publicly accessible
        )
        
        # Construct S3 URL (path-style to avoid SSL issues with dots in bucket name)
        region = Config.AWS_S3_REGION
        # Encode spaces as + to match existing DB URL format (menu+items/...)
        url_key = unique_filename.replace(' ', '+')
        s3_url = f"https://s3.{region}.amazonaws.com/{bucket_name}/{url_key}"
        
        return s3_url
    except ClientError as e:
        print(f"S3 upload error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error during S3 upload: {str(e)}")
        return None


@uploads_bp.route("/image", methods=["POST"])
def upload_image():
    """Upload a single image file to S3 or local storage.
    
    Returns a public URL for the uploaded image.
    """
    if "image" not in request.files:
        return jsonify({"error": "No file part 'image'"}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)

    # Read bytes for upload
    file_bytes = file.read()
    if not file_bytes:
        return jsonify({"error": "Empty file"}), 400

    # Enforce size limit
    max_size = int(current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    content_length = request.content_length or 0
    if content_length and content_length > max_size:
        return jsonify({"error": "File too large", "max_bytes": max_size}), 413
    if len(file_bytes) > max_size:
        return jsonify({"error": "File too large", "max_bytes": max_size}), 413

    # Try S3 upload first
    from config import Config
    if Config.AWS_S3_ENABLED:
        s3_url = upload_to_s3(file_bytes, filename, file.mimetype or "application/octet-stream")
        if s3_url:
            return jsonify({"url": s3_url, "storage": "s3"}), 200
        else:
            return jsonify({"error": "S3 upload failed"}), 500
    
    # Fallback: local storage for development
    print("⚠️  AWS S3 not configured. Using local storage fallback.")
    
    # Reset pointer for save
    file.stream.seek(0)
    
    # Compute uploads directory
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(base, ".."))
    upload_dir = os.path.join(root, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Avoid collisions
    save_path = os.path.join(upload_dir, filename)
    name, ext = os.path.splitext(filename)
    count = 1
    while os.path.exists(save_path):
        filename = f"{name}_{count}{ext}"
        save_path = os.path.join(upload_dir, filename)
        count += 1

    # Save file
    file.save(save_path)

    # Store in database as fallback
    image = UploadedImage(
        filename=filename,
        mime_type=file.mimetype or "application/octet-stream",
        data=file_bytes
    )
    db.session.add(image)
    db.session.commit()

    url_path = f"/api/uploads/image/{image.id}"
    return jsonify({"url": url_path, "storage": "local"}), 200


@uploads_bp.route("/image/<int:image_id>", methods=["GET"])
def get_image(image_id: int):
    """Serve an uploaded image from the database by ID (local storage only)."""
    image = UploadedImage.query.get(image_id)
    if not image:
        return jsonify({"error": "Image not found"}), 404

    return send_file(
        BytesIO(image.data),
        mimetype=image.mime_type,
        download_name=image.filename
    )
