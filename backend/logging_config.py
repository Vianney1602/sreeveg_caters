import logging
import sys
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address
            
        return json.dumps(log_data)


def setup_logging(app):
    """Configure structured logging for the Flask application"""
    
    # Remove default Flask logger handlers
    app.logger.handlers.clear()
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    
    # Add handler to app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Also configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Reduce noise from werkzeug and socketio
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    
    app.logger.info("Structured logging initialized")
