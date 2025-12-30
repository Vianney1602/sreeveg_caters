#!/usr/bin/env python
"""Initialize PostgreSQL database tables for Cater application"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
import models

if __name__ == '__main__':
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("SUCCESS: All database tables created successfully!")
            print("\nTables created:")
            print("- customers")
            print("- orders")
            print("- menu_items")
            print("- event_types")
            print("- order_menu_items")
            print("- monthly_stats")
            print("- contact_inquiries")
        except Exception as e:
            print(f"ERROR: Failed to create tables: {e}")
            sys.exit(1)
