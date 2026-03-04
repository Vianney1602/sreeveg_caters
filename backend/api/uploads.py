from flask import Blueprint, request, jsonify, current_app, send_file
from io import BytesIO
import os
import uuid
from werkzeug.utils import secure_filename
from extensions import db
from models import UploadedImage

uploads_bp = Blueprint("uploads", __name__)

# Initialize S3 clients lazily
_s3_client = None
_s3_presign_client = None
_s3_cors_configured = False

def get_s3_client():
    """Get or create S3 client with real lazy load logic if AWS is configured."""
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


def get_s3_presign_client():
    """Get S3 client configured for path-style pre-signed URLs (needed for dotted bucket names)."""
    global _s3_presign_client
    if _s3_presign_client is None:
        try:
            import boto3
            from botocore.config import Config as BotoConfig
            from config import Config
            if Config.AWS_S3_ENABLED:
                _s3_presign_client = boto3.client(
                    's3',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_S3_REGION,
                    config=BotoConfig(s3={'addressing_style': 'path'})
                )
        except ImportError:
            pass
    return _s3_presign_client


def ensure_s3_cors():
    """Configure CORS on S3 bucket to allow direct browser uploads (idempotent)."""
    global _s3_cors_configured
    if _s3_cors_configured:
        return
    try:
        s3 = get_s3_client()
        if not s3:
            return
        from config import Config
        s3.put_bucket_cors(
            Bucket=Config.AWS_S3_BUCKET_NAME,
            CORSConfiguration={
                'CORSRules': [{
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['PUT', 'GET', 'HEAD'],
                    'AllowedOrigins': [
                        'https://hotelshanmugabhavaan.com',
                        'https://www.hotelshanmugabhavaan.com',
                        'http://localhost:3000',
                        'http://127.0.0.1:3000',
                    ],
                    'MaxAgeSeconds': 86400,
                    'ExposeHeaders': ['ETag'],
                }]
            }
        )
        _s3_cors_configured = True
        print("[OK] S3 bucket CORS configured for direct uploads")
    except Exception as e:
        print(f"[WARN] S3 CORS setup failed (non-fatal): {e}")
        _s3_cors_configured = True  # Don't retry every request

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
            print("S3 client not available")
            return None
        
        from config import Config
        bucket_name = Config.AWS_S3_BUCKET_NAME
        
        # Generate unique key to avoid filename collisions
        file_name_clean = secure_filename(filename)
        name, ext = os.path.splitext(file_name_clean)
        # Add short unique suffix to prevent overwrites
        short_id = uuid.uuid4().hex[:8]
        # Use 'menu items/' prefix to match existing bucket structure
        unique_filename = f"menu items/{name}_{short_id}{ext}"
        
        # Build common upload params
        put_params = {
            'Bucket': bucket_name,
            'Key': unique_filename,
            'Body': file_bytes,
            'ContentType': mime_type,
        }
        
        # Try upload WITHOUT ACL first (works with modern S3 buckets that
        # have ACLs disabled / "Bucket owner enforced" object ownership)
        try:
            s3_client.put_object(**put_params)
        except Exception as acl_err:
            # Fallback: try WITH ACL for legacy buckets
            print(f"S3 upload without ACL failed ({acl_err}), retrying with ACL...")
            put_params['ACL'] = 'public-read'
            s3_client.put_object(**put_params)
        
        # Construct S3 URL (path-style to avoid SSL issues with dots in bucket name)
        region = Config.AWS_S3_REGION
        # Encode spaces as + to match existing DB URL format (menu+items/...)
        url_key = unique_filename.replace(' ', '+')
        s3_url = f"https://s3.{region}.amazonaws.com/{bucket_name}/{url_key}"
        
        print(f"[OK] S3 upload successful: {unique_filename}")
        return s3_url
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"S3 upload failed: {str(e)}")
        return None


@uploads_bp.route("/presign", methods=["POST"])
def presign_upload():
    """Generate a pre-signed S3 URL for direct browser-to-S3 upload.
    
    This bypasses the backend for file transfer — the browser uploads
    directly to S3, making it much faster and avoiding proxy limits.
    
    Request JSON: { "filename": "photo.jpg", "content_type": "image/jpeg" }
    Response: { "upload_url": "https://s3...", "file_url": "https://s3...", "key": "menu items/..." }
    """
    from config import Config
    if not Config.AWS_S3_ENABLED:
        return jsonify({"error": "S3 not configured"}), 503

    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "image.jpg")
    content_type = data.get("content_type", "image/jpeg")

    # Validate extension
    if not allowed_file(filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Generate unique S3 key
    clean = secure_filename(filename)
    name, ext = os.path.splitext(clean)
    short_id = uuid.uuid4().hex[:8]
    key = f"menu items/{name}_{short_id}{ext}"

    # Ensure S3 CORS is configured for direct browser uploads
    ensure_s3_cors()

    try:
        s3 = get_s3_presign_client()
        if not s3:
            return jsonify({"error": "S3 client unavailable"}), 503

        # Generate pre-signed PUT URL (path-style for dotted bucket names)
        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': Config.AWS_S3_BUCKET_NAME,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=300,  # 5 minutes
        )

        # Construct the final public URL for the uploaded file
        region = Config.AWS_S3_REGION
        url_key = key.replace(' ', '+')
        file_url = f"https://s3.{region}.amazonaws.com/{Config.AWS_S3_BUCKET_NAME}/{url_key}"

        return jsonify({
            "upload_url": upload_url,
            "file_url": file_url,
            "key": key,
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate pre-signed URL: {str(e)}"}), 500


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
    s3_url = None
    if Config.AWS_S3_ENABLED:
        s3_url = upload_to_s3(file_bytes, filename, file.mimetype or "application/octet-stream")
        if s3_url:
            return jsonify({"url": s3_url, "storage": "s3"}), 200
        else:
            print("[WARN] S3 upload failed, falling back to local storage...")
    else:
        print("[WARN] AWS S3 not configured. Using local storage fallback.")
    
    # Fallback: local storage (for dev or when S3 fails)
    try:
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

        # Write file bytes directly (stream may have been consumed)
        with open(save_path, 'wb') as f:
            f.write(file_bytes)

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
    except Exception as local_err:
        print(f"Local storage fallback also failed: {local_err}")
        return jsonify({"error": "Image upload failed", "detail": str(local_err)}), 500


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
