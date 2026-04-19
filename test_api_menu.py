#!/usr/bin/env python3
"""Test backend API for menu items"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

try:
    print("Testing /api/menu endpoint...")
    response = requests.get(f"{BASE_URL}/api/menu", timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Items returned: {len(data)}")
        if data:
            print(f"Sample item: {json.dumps(data[0], indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
