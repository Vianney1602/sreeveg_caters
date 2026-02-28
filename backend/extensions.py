from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def emit_with_namespace(*args, **kwargs):
    """Wrapper to safely push socket emissions from background daemon threads by explicitly enforcing the root namespace context."""
    kwargs.setdefault('namespace', '/')
    socketio.emit(*args, **kwargs)
