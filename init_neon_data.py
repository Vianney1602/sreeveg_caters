#!/usr/bin/env python3
"""Initialize database with sample data"""
import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

# Set DATABASE_URL manually
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://neondb_owner:npg_RAl6pUCDeO3J@ep-young-union-a1ulm6vs-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'

from app import create_app, db
from models import MenuItem

app = create_app()

with app.app_context():
    print("\nInitializing Neon database with sample menu items...")
    
    # Create tables if they don't exist
    db.create_all()
    print("✓ Tables created")
    
    # Check if menu items already exist
    existing_items = MenuItem.query.count()
    if existing_items == 0:
        print(f"\nAdding {12} sample menu items...")
        
        items = [
            MenuItem(item_name="Masala Dosa", category=["breads", "south-indian"], price_per_plate=150, is_vegetarian=True, description="Crispy dosa with masala potato filling", stock_quantity=100),
            MenuItem(item_name="Plain Dosa", category=["breads", "south-indian"], price_per_plate=120, is_vegetarian=True, description="Plain crispy dosa", stock_quantity=100),
            MenuItem(item_name="Idly", category=["south-indian"], price_per_plate=80, is_vegetarian=True, description="Steamed rice and lentil cakes", stock_quantity=150),
            MenuItem(item_name="Vada", category=["south-indian"], price_per_plate=100, is_vegetarian=True, description="Fried lentil donuts", stock_quantity=100),
            MenuItem(item_name="Sambhar", category=["curries"], price_per_plate=120, is_vegetarian=True, description="Vegetable curry with lentils", stock_quantity=80),
            MenuItem(item_name="Rasam", category=["curries"], price_per_plate=80, is_vegetarian=True, description="Spicy lentil soup", stock_quantity=120),
            MenuItem(item_name="Biryani - Veg", category=["rice"], price_per_plate=180, is_vegetarian=True, description="Fragrant vegetable biryani", stock_quantity=60),
            MenuItem(item_name="Biryani - Chicken", category=["rice"], price_per_plate=220, is_vegetarian=False, description="Chicken biryani", stock_quantity=50),
            MenuItem(item_name="Curd Rice", category=["rice"], price_per_plate=100, is_vegetarian=True, description="Rice with yogurt", stock_quantity=100),
            MenuItem(item_name="Gulab Jamun", category=["desserts"], price_per_plate=80, is_vegetarian=True, description="Sweet milk solid dumplings", stock_quantity=200),
            MenuItem(item_name="Ice Cream", category=["desserts"], price_per_plate=60, is_vegetarian=True, description="Vanilla or chocolate ice cream", stock_quantity=150),
            MenuItem(item_name="Mango Lassi", category=["beverages"], price_per_plate=70, is_vegetarian=True, description="Mango yogurt drink", stock_quantity=100),
        ]
        
        for item in items:
            db.session.add(item)
            print(f"  ✓ Added: {item.item_name} (₹{item.price_per_plate})")
        
        db.session.commit()
        print(f"\n✅ {len(items)} menu items added successfully!")
    else:
        print(f"✅ Database already has {existing_items} menu items")
    
    print("\n" + "="*70)
