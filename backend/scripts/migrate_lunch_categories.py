"""
Migration script to consolidate lunch menu categories into a single "Lunch Menu" category.
This updates all items from:
- "Lunch Menu - Regular Meals"
- "Lunch Menu - Mini Meals"  
- "Lunch Menu - Variety Rice"

To: "Lunch Menu"
"""

import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import MenuItem

def migrate_lunch_categories():
    """Consolidate all lunch menu subcategories into 'Lunch Menu'"""
    
    old_categories = [
        "Lunch Menu - Regular Meals",
        "Lunch Menu - Mini Meals",
        "Lunch Menu - Variety Rice"
    ]
    
    new_category = "Lunch Menu"
    
    with app.app_context():
        try:
            # Find all items with old lunch categories
            items_to_update = MenuItem.query.filter(
                MenuItem.category.in_(old_categories)
            ).all()
            
            if not items_to_update:
                print("No items found with old lunch categories.")
                return
            
            print(f"Found {len(items_to_update)} items to migrate:")
            
            # Update each item
            for item in items_to_update:
                old_cat = item.category
                item.category = new_category
                print(f"  - {item.item_name}: '{old_cat}' → '{new_category}'")
            
            # Commit changes
            db.session.commit()
            print(f"\n✓ Successfully migrated {len(items_to_update)} items to '{new_category}'")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {e}")
            raise

if __name__ == "__main__":
    print("Starting lunch menu category migration...")
    print("-" * 50)
    migrate_lunch_categories()
    print("-" * 50)
    print("Migration complete!")
