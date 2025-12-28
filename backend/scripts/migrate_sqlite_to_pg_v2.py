"""
Complete Database Migration: SQLite → PostgreSQL
Preserves ALL data (customers, orders, menu items, etc.)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("=" * 70)
    print("DATABASE MIGRATION: SQLite → PostgreSQL")
    print("=" * 70)
    
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        print("\n❌ ERROR: DATABASE_URL not set in .env")
        print("\n📋 Follow these steps:")
        print("   1. Install PostgreSQL from https://www.postgresql.org/download/")
        print("   2. Open PostgreSQL pgAdmin or SQL Shell")
        print("   3. Create database: CREATE DATABASE cater_db;")
        print("   4. Add to backend/.env:")
        print("      DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/cater_db")
        print("   5. Run: python scripts/migrate_sqlite_to_pg.py")
        return
    
    print(f"\n✅ DATABASE_URL is set!")
    
    try:
        import psycopg2
    except ImportError:
        print("\n⏳ Installing psycopg2...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary -q")
        import psycopg2
    
    from app import create_app
    from extensions import db
    from models import Customer, Order, MenuItem, EventType, OrderMenuItem, MonthlyStat, ContactInquiry
    
    # Step 1: Create schema in PostgreSQL
    print("\n🔧 Creating database schema in PostgreSQL...")
    os.environ["DATABASE_URL"] = db_url
    app_pg = create_app()
    
    with app_pg.app_context():
        db.create_all()
        print("   ✅ Schema created in PostgreSQL")
    
    # Step 2: Read SQLite
    print("\n📖 Reading data from SQLite...")
    os.environ.pop("DATABASE_URL", None)
    app_sqlite = create_app()
    
    with app_sqlite.app_context():
        customers = Customer.query.all()
        orders = Order.query.all()
        order_items = OrderMenuItem.query.all()
        menu_items = MenuItem.query.all()
        event_types = EventType.query.all()
        stats = MonthlyStat.query.all()
        inquiries = ContactInquiry.query.all()
        
        print(f"   📊 Found {len(customers)} customers")
        print(f"   📦 Found {len(orders)} orders")
        print(f"   🛒 Found {len(order_items)} order items")
        print(f"   🍽️  Found {len(menu_items)} menu items")
        print(f"   🎊 Found {len(event_types)} event types")
        print(f"   📈 Found {len(stats)} monthly stats")
        print(f"   💬 Found {len(inquiries)} inquiries")
    
    # Step 3: Write to PostgreSQL
    print("\n✍️  Migrating data to PostgreSQL...")
    os.environ["DATABASE_URL"] = db_url
    app_pg = create_app()
    
    with app_pg.app_context():
        # Add customers
        for c in customers:
            db.session.merge(c)
        db.session.commit()
        print(f"   ✅ Migrated {len(customers)} customers")
        
        # Add menu items
        for m in menu_items:
            db.session.merge(m)
        db.session.commit()
        print(f"   ✅ Migrated {len(menu_items)} menu items")
        
        # Add event types
        for e in event_types:
            db.session.merge(e)
        db.session.commit()
        print(f"   ✅ Migrated {len(event_types)} event types")
        
        # Add orders (must be after customers)
        for o in orders:
            db.session.merge(o)
        db.session.commit()
        print(f"   ✅ Migrated {len(orders)} orders")
        
        # Add order items (must be after orders & menu items)
        for oi in order_items:
            db.session.merge(oi)
        db.session.commit()
        print(f"   ✅ Migrated {len(order_items)} order items")
        
        # Add stats
        for s in stats:
            db.session.merge(s)
        db.session.commit()
        print(f"   ✅ Migrated {len(stats)} monthly stats")
        
        # Add inquiries
        for i in inquiries:
            db.session.merge(i)
        db.session.commit()
        print(f"   ✅ Migrated {len(inquiries)} inquiries")
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print("\n📍 All your data is now in PostgreSQL!")
    print("\n🎯 Next steps:")
    print("   1. Restart your backend server")
    print("   2. Test the website to ensure everything works")
    print("   3. Keep database.db as backup (you can delete it later)")
    

if __name__ == '__main__':
    main()
