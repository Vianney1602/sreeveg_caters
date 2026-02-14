import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Database configuration - supports both SQLite (dev) and PostgreSQL (production)
    # For production, set DATABASE_URL environment variable to your PostgreSQL connection string
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if DATABASE_URL:
        # Fix for Heroku/Railway postgres:// -> postgresql:// 
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Development: SQLite
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pool settings for better performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,              # Number of connections to keep open
        'pool_recycle': 3600,         # Recycle connections after 1 hour
        'pool_pre_ping': True,        # Verify connections before using
        'max_overflow': 20,           # Extra connections when pool is full
        'pool_timeout': 30,           # Timeout for getting connection from pool
    }
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    
    # Session configuration for production
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", "3600"))  # seconds
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    
    # Hardcoded admin credentials for website owner only
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "hotelshanmugabhavaan@gmail.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    ADMIN_EMAIL = os.environ.get("ADMIN_USERNAME", "hotelshanmugabhavaan@gmail.com")

    # Upload limits and allowed image types
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))  # 5 MB
    ALLOWED_IMAGE_EXTENSIONS = set(
        (os.environ.get("ALLOWED_IMAGE_EXTENSIONS", "png,jpg,jpeg,gif,webp")).split(",")
    )

    # Brevo (Sendinblue) configuration for transactional emails
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "noreply@hotelshanmugabhavaan.com")
    BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Hotel Shanmuga Bhavaan")

    # CORS allowed origins (comma-separated). In production, set to your domains only.
    CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        ",".join([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://localhost:3000",
            "https://127.0.0.1:3000",
        ])
    )

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_REGION = os.environ.get("AWS_S3_REGION", "us-east-1")
    AWS_S3_ENABLED = (
        AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_BUCKET_NAME
    )

    @staticmethod
    def parse_origins(origins_str: str):
        return [o.strip() for o in (origins_str or "").split(",") if o.strip()]
