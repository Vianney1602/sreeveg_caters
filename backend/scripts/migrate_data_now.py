"""
Migrate data from SQLite to PostgreSQL
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("=" * 70)
    print("MIGRATING DATA: SQLite → PostgreSQL")
    print("=" * 70)
    
    # Read from SQLite directly
    print("\n📖 Reading from SQLite (database.db)...")
    sqlite_conn = sqlite3.connect('database.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Read all data
    cursor.execute("SELECT * FROM menu_items")
    menu_items = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM event_types")
    event_types = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM customers")
    customers = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM orders")
    orders = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM order_menu_items")
    order_items = [dict(row) for row in cursor.fetchall()]
    
    sqlite_conn.close()
    
    print(f"   ✅ Found {len(menu_items)} menu items")
    print(f"   ✅ Found {len(event_types)} event types")
    print(f"   ✅ Found {len(customers)} customers")
    print(f"   ✅ Found {len(orders)} orders")
    print(f"   ✅ Found {len(order_items)} order items")
    
    # Write to PostgreSQL
    print("\n✍️  Writing to PostgreSQL...")
    from app import create_app
    from extensions import db
    from models import MenuItem, EventType, Customer, Order, OrderMenuItem
    
    app = create_app()
    with app.app_context():
        # Clear existing data
        OrderMenuItem.query.delete()
        Order.query.delete()
        Customer.query.delete()
        MenuItem.query.delete()
        EventType.query.delete()
        db.session.commit()
        
        # Insert event types
        for et in event_types:
            event = EventType(
                event_type_id=et['event_type_id'],
                event_name=et['event_name'],
                minimum_guests=et['minimum_guests'],
                description=et.get('description'),
                image_url=et.get('image_url')
            )
            db.session.add(event)
        db.session.commit()
        print(f"   ✅ Migrated {len(event_types)} event types")
        
        # Insert menu items
        for mi in menu_items:
            item = MenuItem(
                item_id=mi['item_id'],
                item_name=mi['item_name'],
                category=mi['category'],
                price_per_plate=mi['price_per_plate'],
                is_vegetarian=bool(mi['is_vegetarian']),
                image_url=mi.get('image_url'),
                description=mi.get('description'),
                is_available=bool(mi.get('is_available', 1)),
                stock_quantity=mi.get('stock_quantity', 100)
            )
            db.session.add(item)
        db.session.commit()
        print(f"   ✅ Migrated {len(menu_items)} menu items")
        
        # Insert customers
        for c in customers:
            customer = Customer(
                customer_id=c['customer_id'],
                full_name=c['full_name'],
                phone_number=c['phone_number'],
                email=c.get('email'),
                password_hash=c.get('password_hash'),
                created_at=c.get('created_at'),
                total_orders_count=c.get('total_orders_count', 0)
            )
            db.session.add(customer)
        db.session.commit()
        print(f"   ✅ Migrated {len(customers)} customers")
        
        # Insert orders
        for o in orders:
            order = Order(
                order_id=o['order_id'],
                customer_id=o.get('customer_id'),
                customer_name=o.get('customer_name'),
                phone_number=o.get('phone_number'),
                email=o.get('email'),
                event_type=o.get('event_type'),
                number_of_guests=o.get('number_of_guests', 0),
                event_date=o.get('event_date'),
                event_time=o.get('event_time'),
                venue_address=o.get('venue_address'),
                special_requirements=o.get('special_requirements'),
                status=o.get('status', 'Pending'),
                total_amount=o.get('total_amount', 0),
                razorpay_order_id=o.get('razorpay_order_id'),
                payment_method=o.get('payment_method', 'online'),
                created_at=o.get('created_at'),
                updated_at=o.get('updated_at')
            )
            db.session.add(order)
        db.session.commit()
        print(f"   ✅ Migrated {len(orders)} orders")
        
        # Insert order items
        valid_menu_ids = {mi['item_id'] for mi in menu_items}
        skipped = 0
        for oi in order_items:
            if oi['menu_item_id'] not in valid_menu_ids:
                skipped += 1
                continue
            order_item = OrderMenuItem(
                order_menu_id=oi.get('order_menu_id'),
                order_id=oi['order_id'],
                menu_item_id=oi['menu_item_id'],
                quantity=oi['quantity'],
                price_at_order_time=oi.get('price_at_order_time')
            )
            db.session.add(order_item)
        db.session.commit()
        print(f"   ✅ Migrated {len(order_items) - skipped} order items (skipped {skipped} with invalid menu_item_id)")
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print(f"\nMigrated {len(menu_items)} menu items to PostgreSQL!")
    print("Your website should now show all the menu items.")

if __name__ == '__main__':
    main()
