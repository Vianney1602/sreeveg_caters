#!/usr/bin/env python3
"""Check menu data in database"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')

# Test database connection
from sqlalchemy import create_engine, text
db_url = os.environ.get('DATABASE_URL')
print(f"Database URL: {db_url[:50] if db_url else 'NOT SET'}...")

if db_url:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM menu_items"))
            count = result.scalar()
            print(f"✅ Database connected. Menu items: {count}")
            
            # List items
            result = conn.execute(text("SELECT item_id, item_name, price_per_plate FROM menu_items LIMIT 5"))
            for row in result:
                print(f"  - {row[0]}: {row[1]} (₹{row[2]})")
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ DATABASE_URL not set")
