#!/usr/bin/env python3
"""
Migration script to convert menu items from single category (string) 
to multiple categories (array/list).

This script consolidates duplicate items (same name but different categories)
into single items with multiple categories.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from models import MenuItem
from app import app
import json

def normalize_name(name):
    """Normalize item name for comparison"""
    return name.strip().lower()


def to_list(category_value):
    """Convert stored category value into a list, handling legacy string formats."""
    if isinstance(category_value, list):
        return category_value
    if isinstance(category_value, str):
        stripped = category_value.strip()
        # Handle stringified JSON lists
        if stripped.startswith('[') and stripped.endswith(']'):
            try:
                loaded = json.loads(stripped)
                if isinstance(loaded, list):
                    return loaded
            except Exception:
                pass
        # Fallback: wrap single string
        return [category_value]
    return []

def migrate_items():
    """Migrate items to multi-category format"""
    try:
        # Get all items
        all_items = MenuItem.query.all()
        
        if not all_items:
            print("No items found in database")
            return
        
        print(f"Found {len(all_items)} items to process")
        
        # Group items by normalized name
        items_by_name = {}
        for item in all_items:
            normalized = normalize_name(item.item_name)
            if normalized not in items_by_name:
                items_by_name[normalized] = []
            items_by_name[normalized].append(item)
        
        items_to_delete = []
        items_to_update = []
        
        # Process groups with multiple items (duplicates)
        for normalized_name, items in items_by_name.items():
            if len(items) > 1:
                print(f"\nFound duplicate: '{items[0].item_name}' ({len(items)} entries)")
                
                # Keep the first item, consolidate categories
                primary_item = items[0]
                categories = []
                
                for item in items:
                    categories.extend(to_list(item.category))
                    
                    # Mark duplicates for deletion
                    if item.item_id != primary_item.item_id:
                        items_to_delete.append(item.item_id)
                    
                    print(f"  - ID {item.item_id}: {item.category}")
                
                # Remove duplicates and update primary item
                unique_categories = list(dict.fromkeys(categories))  # Maintain order, remove dupes
                primary_item.category = unique_categories
                items_to_update.append((primary_item.item_id, unique_categories))
                print(f"  → Consolidating to: {unique_categories}")
            else:
                # Single item - just ensure category is a list
                item = items[0]
                parsed = to_list(item.category)
                if parsed != item.category:
                    item.category = parsed
                    items_to_update.append((item.item_id, item.category))
                    print(f"Converting '{item.item_name}' to array: {item.category}")
        
        # Apply updates
        if items_to_update:
            print(f"\nUpdating {len(items_to_update)} items...")
            for item_id, categories in items_to_update:
                item = MenuItem.query.get(item_id)
                if item:
                    item.category = categories
                    db.session.add(item)
            db.session.commit()
            print(f"✓ Updated {len(items_to_update)} items")
        
        # Delete duplicates
        if items_to_delete:
            print(f"\nDeleting {len(items_to_delete)} duplicate items...")
            for item_id in items_to_delete:
                item = MenuItem.query.get(item_id)
                if item:
                    db.session.delete(item)
            db.session.commit()
            print(f"✓ Deleted {len(items_to_delete)} items")
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        db.session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    with app.app_context():
        migrate_items()
