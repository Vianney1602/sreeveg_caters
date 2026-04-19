#!/usr/bin/env python3
"""
Test script to verify Razorpay integration is working properly
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 10

print("=" * 70)
print("RAZORPAY INTEGRATION TEST")
print("=" * 70)

# Check if Razorpay credentials are configured
print("\n1. Checking Razorpay Credentials Configuration...")
print("-" * 70)

key_id = os.environ.get("RAZORPAY_KEY_ID")
key_secret = os.environ.get("RAZORPAY_KEY_SECRET")

if key_id and key_secret:
    print(f"✅ RAZORPAY_KEY_ID: {key_id[:10]}...{key_id[-5:]}")
    print(f"✅ RAZORPAY_KEY_SECRET: {key_secret[:10]}...{key_secret[-5:]}")
    print("✅ Razorpay credentials are configured!")
else:
    print("❌ Razorpay credentials are NOT configured!")
    print(f"   KEY_ID: {key_id}")
    print(f"   KEY_SECRET: {key_secret}")
    exit(1)

# Test 1: Create an order on the backend
print("\n2. Testing Order Creation...")
print("-" * 70)

order_data = {
    "customer_name": "Test Customer",
    "phone_number": "9876543210",
    "email": "test@example.com",
    "delivery_date": "2026-04-20",
    "delivery_time": "12:00",
    "delivery_address": "123 Test Street",
    "menu_items": [
        {
            "menu_id": 1,
            "item_name": "Masala Dosa",
            "quantity": 2,
            "unit_price": 150.00
        }
    ],
    "payment_method": "online"
}

try:
    response = requests.post(f"{BACKEND_URL}/api/orders", json=order_data, timeout=API_TIMEOUT)
    print(f"Order Creation Response Status: {response.status_code}")
    
    if response.status_code == 201:
        order_response = response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order ID: {order_response.get('order_id')}")
        print(f"   Total Amount: ₹{order_response.get('total_amount')}")
        
        order_id = order_response.get('order_id')
        total_amount = order_response.get('total_amount')
        
        # Test 2: Create Razorpay order
        print("\n3. Testing Razorpay Order Creation...")
        print("-" * 70)
        
        razorpay_order_data = {
            "order_id": order_id,
            "amount": total_amount
        }
        
        try:
            razorpay_response = requests.post(
                f"{BACKEND_URL}/api/payments/create_order",
                json=razorpay_order_data,
                timeout=API_TIMEOUT
            )
            print(f"Razorpay Order Response Status: {razorpay_response.status_code}")
            print(f"Response: {json.dumps(razorpay_response.json(), indent=2)}")
            
            if razorpay_response.status_code == 200:
                rzp_order = razorpay_response.json()
                razorpay_order_id = rzp_order.get('order_id')
                print(f"✅ Razorpay order created successfully!")
                print(f"   Razorpay Order ID: {razorpay_order_id}")
                print(f"   Amount: ₹{rzp_order.get('amount') / 100.0}")
                print(f"   Currency: {rzp_order.get('currency')}")
                print("\n✅ Razorpay integration appears to be WORKING!")
            else:
                print(f"❌ Razorpay order creation FAILED")
                if 'error' in razorpay_response.json():
                    print(f"   Error: {razorpay_response.json().get('error')}")
                if 'details' in razorpay_response.json():
                    print(f"   Details: {razorpay_response.json().get('details')}")
                    
        except Exception as e:
            print(f"❌ Error creating Razorpay order: {str(e)}")
    else:
        print(f"❌ Order creation failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error creating order: {str(e)}")
    print("\nNote: Make sure the backend server is running on http://127.0.0.1:8000")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
