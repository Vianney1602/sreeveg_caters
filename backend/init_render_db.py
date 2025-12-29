#!/usr/bin/env python
"""
Initialize Render PostgreSQL database with tables if they don't exist.
This script is called automatically when the app starts.
"""

import os
import sys
from app import create_app, db

def init_db():
    """Create all database tables if they don't exist."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables defined in models
            db.create_all()
            print("✓ Database tables created successfully!")
            return True
        except Exception as e:
            print(f"✗ Error creating database tables: {e}")
            return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
