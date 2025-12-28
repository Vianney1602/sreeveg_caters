from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename

uploads_bp = Blueprint("uploads", __name__)

def _allowed_extensions():
    exts = current_app.config.get("ALLOWED_IMAGE_EXTENSIONS")
    if isinstance(exts, (set, list, tuple)):
        return set(map(str.lower, exts))
    if isinstance(exts, str):
        return set(x.strip().lower() for x in exts.split(",") if x.strip())
    return {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _allowed_extensions()


@uploads_bp.route("/image", methods=["POST"])
def upload_image():
    """Upload a single image file and return its public URL.

    Saves to backend/static/uploads and returns a URL like /static/uploads/<filename>.
    """
    if "image" not in request.files:
        return jsonify({"error": "No file part 'image'"}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)

    # Compute uploads directory: backend/static/uploads
    base = os.path.dirname(os.path.abspath(__file__))  # .../backend/api
    root = os.path.abspath(os.path.join(base, ".."))  # .../backend
    upload_dir = os.path.join(root, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Avoid collisions by suffixing _1, _2, ...
    save_path = os.path.join(upload_dir, filename)
    name, ext = os.path.splitext(filename)
    count = 1
    while os.path.exists(save_path):
        filename = f"{name}_{count}{ext}"
        save_path = os.path.join(upload_dir, filename)
        count += 1

    # Enforce size limit: stream check (Content-Length) and runtime cap
    max_size = int(current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    content_length = request.content_length or 0
    if content_length and content_length > max_size:
        return jsonify({"error": "File too large", "max_bytes": max_size}), 413

    # Save file safely
    file.save(save_path)

    url_path = f"/static/uploads/{filename}"
    return jsonify({"url": url_path})
