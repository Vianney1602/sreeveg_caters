import os
import sys
from sqlalchemy import text
from flask import Flask

# Add the parent directory to sys.path to allow importing from backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from extensions import db
except ImportError as e:
    print(f"Error: Could not import backend modules. Make sure you are running this from the backend directory. {e}")
    sys.exit(1)

def optimize_database():
    app = create_app()
    with app.app_context():
        print(f"Starting database optimization on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Index for faster order lookups by customer
        # 2. Index for faster status filtering (Overview page)
        # 3. Index for chronological sorting
        # 4. Index for customer email lookups (Login/Forgot PW)
        
        indexes = [
            ("idx_orders_customer_id", "orders", "customer_id"),
            ("idx_orders_status", "orders", "status"),
            ("idx_orders_created_at", "orders", "created_at"),
            ("idx_customers_email", "customers", "email"),
            ("idx_order_menu_items_order_id", "order_menu_items", "order_id")
        ]
        
        is_postgres = "postgresql" in app.config['SQLALCHEMY_DATABASE_URI'].lower()
        
        for idx_name, table, column in indexes:
            try:
                print(f"Adding index {idx_name} to {table}({column})...")
                
                if is_postgres:
                    # PostgreSQL syntax with 'IF NOT EXISTS' requires newer versions, 
                    # better to catch the exception if it already exists
                    sql = text(f"CREATE INDEX {idx_name} ON {table} ({column})")
                else:
                    # SQLite syntax
                    sql = text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})")
                
                db.session.execute(sql)
                db.session.commit()
                print(f"Successfully added index {idx_name}.")
            except Exception as e:
                db.session.rollback()
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"Index {idx_name} already exists. Skipping.")
                else:
                    print(f"Error adding index {idx_name}: {e}")

        print("\nDatabase optimization complete! Your Admin Dashboard queries should now be significantly faster.")

if __name__ == "__main__":
    optimize_database()
