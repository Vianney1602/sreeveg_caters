"""
Database Migration Script: SQLite → PostgreSQL
This script safely migrates all data from SQLite to PostgreSQL while preserving everything.

Usage:
    1. Install PostgreSQL locally (or use a service like render.com)
    2. Create a PostgreSQL database
    3. Update DATABASE_URL below
    4. Run: python scripts/migrate_to_postgresql.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import (
    Customer, Order, MenuItem, EventType, 
    OrderMenuItem, MonthlyStat, ContactInquiry
)

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Step 1: Create app with current config (SQLite)
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("DATABASE MIGRATION: SQLite → PostgreSQL")
        print("=" * 60)
        
        # Step 2: Count existing data
        print("\n📊 Current Data in SQLite:")
        print(f"   Customers: {Customer.query.count()}")
        print(f"   Orders: {Order.query.count()}")
        print(f"   Menu Items: {MenuItem.query.count()}")
        print(f"   Event Types: {EventType.query.count()}")
        print(f"   Order Items: {OrderMenuItem.query.count()}")
        print(f"   Monthly Stats: {MonthlyStat.query.count()}")
        print(f"   Contact Inquiries: {ContactInquiry.query.count()}")
        
        # Step 3: Export data to dictionaries (in-memory)
        print("\n📥 Exporting data from SQLite...")
        
        customers = [{
            'customer_id': c.customer_id,
            'customer_name': c.customer_name,
            'phone_number': c.phone_number,
            'email': c.email,
            'address': c.address,
            'total_orders': c.total_orders,
            'created_at': c.created_at
        } for c in Customer.query.all()]
        
        menu_items = [{
            'item_id': m.item_id,
            'item_name': m.item_name,
            'category': m.category,
            'price_per_plate': m.price_per_plate,
            'is_vegetarian': m.is_vegetarian,
            'image_url': m.image_url,
            'description': m.description,
            'stock_quantity': m.stock_quantity,
            'is_available': m.is_available
        } for m in MenuItem.query.all()]
        
        event_types = [{
            'event_type_id': e.event_type_id,
            'event_name': e.event_name,
            'minimum_guests': e.minimum_guests,
            'description': e.description,
            'image_url': e.image_url
        } for e in EventType.query.all()]
        
        orders = [{
            'order_id': o.order_id,
            'customer_id': o.customer_id,
            'customer_name': o.customer_name,
            'phone_number': o.phone_number,
            'email': o.email,
            'venue_address': o.venue_address,
            'event_date': o.event_date,
            'event_type': o.event_type,
            'total_amount': o.total_amount,
            'status': o.status,
            'payment_status': o.payment_status,
            'payment_method': o.payment_method,
            'razorpay_order_id': o.razorpay_order_id,
            'created_at': o.created_at
        } for o in Order.query.all()]
        
        order_items = [{
            'order_menu_id': oi.order_menu_id,
            'order_id': oi.order_id,
            'menu_item_id': oi.menu_item_id,
            'quantity': oi.quantity,
            'price_at_order_time': oi.price_at_order_time
        } for oi in OrderMenuItem.query.all()]
        
        monthly_stats = [{
            'stat_id': s.stat_id,
            'month': s.month,
            'year': s.year,
            'total_orders': s.total_orders,
            'total_revenue': s.total_revenue,
            'total_guests': s.total_guests
        } for s in MonthlyStat.query.all()]
        
        contact_inquiries = [{
            'inquiry_id': c.inquiry_id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'message': c.message,
            'created_at': c.created_at
        } for c in ContactInquiry.query.all()]
        
        print(f"   ✅ Exported {len(customers)} customers")
        print(f"   ✅ Exported {len(orders)} orders")
        print(f"   ✅ Exported {len(order_items)} order items")
        print(f"   ✅ Exported {len(menu_items)} menu items")
        print(f"   ✅ Exported {len(event_types)} event types")
        print(f"   ✅ Exported {len(monthly_stats)} monthly stats")
        print(f"   ✅ Exported {len(contact_inquiries)} contact inquiries")
        
        return {
            'customers': customers,
            'orders': orders,
            'order_items': order_items,
            'menu_items': menu_items,
            'event_types': event_types,
            'monthly_stats': monthly_stats,
            'contact_inquiries': contact_inquiries
        }


def import_data_to_postgresql(data):
    """Import exported data to PostgreSQL"""
    
    print("\n⚙️  IMPORTANT: Next steps:")
    print("   1. Install PostgreSQL (if not already installed)")
    print("   2. Create a PostgreSQL database: createdb cater_db")
    print("   3. Update DATABASE_URL in .env:")
    print("      DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cater_db")
    print("   4. Run: python scripts/migrate_to_postgresql.py --import")
    print("   5. That's it! All your data will be imported!")
    
    # If called with --import flag, actually do the import
    if len(sys.argv) > 1 and sys.argv[1] == '--import':
        print("\n⚠️  WARNING: Make sure you've set DATABASE_URL in .env")
        input("Press Enter to continue with migration (this cannot be undone)...")
        
        # Create app with PostgreSQL config
        os.environ['MIGRATING'] = '1'  # Flag to indicate we're migrating
        from importlib import reload
        import config as config_module
        reload(config_module)
        
        app = create_app()
        
        with app.app_context():
            print("\n🗄️  Creating PostgreSQL tables...")
            db.create_all()
            
            print("📥 Importing customers...")
            for customer_data in data['customers']:
                customer = Customer(**customer_data)
                db.session.add(customer)
            db.session.commit()
            print(f"   ✅ Imported {len(data['customers'])} customers")
            
            print("📥 Importing menu items...")
            for item_data in data['menu_items']:
                item = MenuItem(**item_data)
                db.session.add(item)
            db.session.commit()
            print(f"   ✅ Imported {len(data['menu_items'])} menu items")
            
            print("📥 Importing event types...")
            for event_data in data['event_types']:
                event = EventType(**event_data)
                db.session.add(event)
            db.session.commit()
            print(f"   ✅ Imported {len(data['event_types'])} event types")
            
            print("📥 Importing orders...")
            for order_data in data['orders']:
                order = Order(**order_data)
                db.session.add(order)
            db.session.commit()
            print(f"   ✅ Imported {len(data['orders'])} orders")
            
            print("📥 Importing order items...")
            for item_data in data['order_items']:
                order_item = OrderMenuItem(**item_data)
                db.session.add(order_item)
            db.session.commit()
            print(f"   ✅ Imported {len(data['order_items'])} order items")
            
            print("📥 Importing monthly statistics...")
            for stat_data in data['monthly_stats']:
                stat = MonthlyStat(**stat_data)
                db.session.add(stat)
            db.session.commit()
            print(f"   ✅ Imported {len(data['monthly_stats'])} monthly stats")
            
            print("📥 Importing contact inquiries...")
            for inquiry_data in data['contact_inquiries']:
                inquiry = ContactInquiry(**inquiry_data)
                db.session.add(inquiry)
            db.session.commit()
            print(f"   ✅ Imported {len(data['contact_inquiries'])} contact inquiries")
            
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 60)
            print("\n✨ All your data has been safely moved to PostgreSQL!")
            print("\n🎯 Next steps:")
            print("   1. Restart your backend server")
            print("   2. Test that everything works")
            print("   3. You can now delete database.db (SQLite file)")


if __name__ == '__main__':
    data = migrate_data()
    import_data_to_postgresql(data)
