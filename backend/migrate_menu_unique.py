"""
Migration script to:
1. Add UNIQUE constraint on menu_items.item_name (prevents duplicate items at DB level)
2. Change image_url column from VARCHAR(255) to TEXT (future-proof for long URLs)

Safe to run multiple times (idempotent).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        conn = db.engine.connect()
        
        # 1. Change image_url to TEXT (PostgreSQL: ALTER TYPE is safe even if already TEXT)
        try:
            conn.execute(text(
                "ALTER TABLE menu_items ALTER COLUMN image_url TYPE TEXT"
            ))
            conn.commit()
            print("[OK] image_url column changed to TEXT")
        except Exception as e:
            conn.rollback()
            print(f"[SKIP] image_url type change: {e}")
        
        # 2. Add unique constraint on item_name (if not already present)
        try:
            # Check if constraint already exists
            result = conn.execute(text("""
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'menu_items' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name = 'uq_menu_items_item_name'
            """))
            if result.fetchone():
                print("[SKIP] Unique constraint on item_name already exists")
            else:
                conn.execute(text(
                    "ALTER TABLE menu_items ADD CONSTRAINT uq_menu_items_item_name UNIQUE (item_name)"
                ))
                conn.commit()
                print("[OK] Unique constraint added on item_name")
        except Exception as e:
            conn.rollback()
            # Might fail if duplicates still exist
            print(f"[WARN] Could not add unique constraint: {e}")
            print("       Make sure there are no duplicate item names first!")
        
        conn.close()
        print("\nMigration complete.")

if __name__ == "__main__":
    migrate()
