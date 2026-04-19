#!/usr/bin/env python3
"""Quick test to check order creation endpoint"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

# Test payload matching what the frontend sends
test_payload = {
    "customer_name": "Test User",
    "phone_number": "9876543210",
    "email": "test@example.com",
    "event_type": "Delivery",
    "guests": 1,
    "event_date": "2026-04-19",
    "event_time": "14:00",
    "venue": "Chennai",
    "special": None,
    "total_amount": 15.00,
    "payment_method": "online",
    "menu_items": [
        {
            "id": 1,  # Assuming menu item ID 1 exists
            "qty": 1,
            "price": 15.00
        }
    ]
}

print("Testing Order Creation Endpoint...")
print("Payload:", json.dumps(test_payload, indent=2))

try:
    response = requests.post(
        f"{BACKEND_URL}/api/orders",
        json=test_payload,
        timeout=10
    )
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Make sure backend is running on http://127.0.0.1:8000")
