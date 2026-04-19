#!/usr/bin/env python3
"""Check Neon PostgreSQL database for menu items and orders"""
import os
import sys

# Change to backend directory first
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

from app import create_app
from models import MenuItem, Order, Customer

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("NEON POSTGRESQL DATABASE CHECK")
    print("="*70)
    
    # Check menu items
    print("\n1. MENU ITEMS:")
    print("-"*70)
    menu_items = MenuItem.query.all()
    print(f"Total menu items: {len(menu_items)}\n")
    
    if menu_items:
        for item in menu_items[:15]:  # Show first 15
            print(f"  ✓ ID: {item.item_id:2d} | Name: {item.item_name:30s} | Price: ₹{item.price_per_plate:7.2f} | Stock: {item.stock_quantity:3d} | Available: {item.is_available}")
    else:
        print("  ⚠️ No menu items found!")
    
    # Check customers
    print("\n2. CUSTOMERS:")
    print("-"*70)
    customers = Customer.query.all()
    print(f"Total customers: {len(customers)}\n")
    
    if customers:
        for customer in customers[:10]:
            print(f"  ✓ ID: {customer.customer_id:3d} | Name: {customer.full_name:25s} | Email: {customer.email}")
    
    # Check orders
    print("\n3. ORDERS:")
    print("-"*70)
    orders = Order.query.all()
    print(f"Total orders: {len(orders)}\n")
    
    if orders:
        for order in orders[-10:]:  # Show last 10
            print(f"  ✓ Order ID: {order.order_id:4d} | Customer: {order.customer_name:25s} | Amount: ₹{order.total_amount:8.2f} | Status: {order.status:10s} | Payment: {order.payment_method}")
    
    print("\n" + "="*70)
