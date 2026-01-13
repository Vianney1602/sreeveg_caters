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
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin@shanmugabhavaan.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    ADMIN_EMAIL = "admin@shanmugabhavaan.com"

    # Upload limits and allowed image types
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))  # 5 MB
    ALLOWED_IMAGE_EXTENSIONS = set(
        (os.environ.get("ALLOWED_IMAGE_EXTENSIONS", "png,jpg,jpeg,gif,webp")).split(",")
    )

    # Flask-Mail configuration for OTP emails
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

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

    @staticmethod
    def parse_origins(origins_str: str):
        return [o.strip() for o in (origins_str or "").split(",") if o.strip()]
