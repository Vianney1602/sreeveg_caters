#!/usr/bin/env python3
"""Check if menu items exist in the database"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from backend.app import create_app
from backend.models import MenuItem

app = create_app()

with app.app_context():
    menu_items = MenuItem.query.all()
    print(f"Total menu items in database: {len(menu_items)}")
    
    if menu_items:
        print("\nMenu Items:")
        for item in menu_items[:10]:  # Show first 10
            print(f"  - ID: {item.item_id}, Name: {item.item_name}, Price: {item.price_per_plate}, Stock: {item.stock_quantity}, Available: {item.is_available}")
    else:
        print("⚠️ No menu items found in database!")
        print("You need to run init_tables.py to populate the database")
