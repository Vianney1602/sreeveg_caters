"""
Script to find and remove duplicate menu items from the database.
Keeps the oldest entry (lowest item_id) for each item name.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import MenuItem
from sqlalchemy import func

def remove_duplicates():
    with app.app_context():
        # Find all items
        all_items = MenuItem.query.order_by(MenuItem.item_id).all()
        print(f"\nTotal menu items in database: {len(all_items)}")
        
        # Group by normalized name (case-insensitive, stripped)
        seen = {}
        duplicates = []
        
        for item in all_items:
            key = item.item_name.strip().lower()
            if key in seen:
                duplicates.append(item)
                print(f"  DUPLICATE: id={item.item_id}, name='{item.item_name}', image='{item.image_url or 'none'}'")
            else:
                seen[key] = item
                print(f"  KEEP:      id={item.item_id}, name='{item.item_name}', image='{item.image_url or 'none'}'")
        
        if not duplicates:
            print("\nNo duplicates found!")
            return
        
        print(f"\n--- Found {len(duplicates)} duplicate(s) to remove ---")
        
        # Delete duplicates
        for dup in duplicates:
            print(f"  Deleting id={dup.item_id}, name='{dup.item_name}'")
            db.session.delete(dup)
        
        db.session.commit()
        
        # Verify
        remaining = MenuItem.query.count()
        print(f"\nDone! Remaining menu items: {remaining}")

if __name__ == "__main__":
    remove_duplicates()
