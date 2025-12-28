"""
WSGI entry point for production deployment.
Used by Gunicorn and other WSGI servers.
"""
from app import create_app, socketio

app = create_app()

# Expose the Flask app object for WSGI servers (gunicorn/uwsgi)
app_for_gunicorn = app

if __name__ == "__main__":
    # Local run uses Socket.IO server entrypoint
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
