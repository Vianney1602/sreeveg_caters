#!/usr/bin/env python
"""
Test script for OTP flow - test forgot-password, verify-otp, and reset-password
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/users"
TEST_EMAIL = "vianneyinfantraj1602@gmail.com"
TEST_PASSWORD = "TestPassword123!"
NEW_PASSWORD = "NewPassword456!"

def test_register():
    """Register a test user"""
    print("\n[1] Testing user registration...")
    payload = {
        "name": "Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "phone": "9876543210"
    }
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201 or "already exists" in response.text
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_forgot_password():
    """Test forgot-password endpoint"""
    print("\n[2] Testing forgot-password endpoint...")
    payload = {"email": TEST_EMAIL}
    try:
        response = requests.post(f"{BASE_URL}/forgot-password", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_verify_otp(otp):
    """Test verify-otp endpoint"""
    print(f"\n[3] Testing verify-otp endpoint with OTP: {otp}...")
    payload = {
        "email": TEST_EMAIL,
        "otp": otp
    }
    try:
        response = requests.post(f"{BASE_URL}/verify-otp", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_reset_password(otp):
    """Test reset-password endpoint"""
    print(f"\n[4] Testing reset-password endpoint with OTP: {otp}...")
    payload = {
        "email": TEST_EMAIL,
        "otp": otp,
        "new_password": NEW_PASSWORD
    }
    try:
        response = requests.post(f"{BASE_URL}/reset-password", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("OTP Flow Testing Script")
    print("="*60)
    
    # Step 1: Register user
    if not test_register():
        print("\n[ERROR] User registration failed or user already exists")
    
    # Step 2: Request OTP
    if not test_forgot_password():
        print("\n[ERROR] forgot-password failed")
    else:
        print("\n[SUCCESS] OTP request sent successfully!")
        
        # For testing, we'll need to check the console output or logs for the actual OTP
        # If Redis is working, OTP should be stored there
        # If not, it should print to console
        
        # Manually prompt for OTP (in real scenario, would retrieve from email or Redis)
        print("\n[INFO] Check Flask console output above for the OTP code (6 digits)")
        print("[INFO] Waiting 2 seconds for user to note the OTP...")
        time.sleep(2)
        
        # For automated testing, we can try to get OTP from the system
        # But first let's just try with a test OTP to show the flow
        test_otp = input("\nEnter the OTP code displayed above: ").strip()
        
        if test_otp and len(test_otp) == 6 and test_otp.isdigit():
            # Step 3: Verify OTP
            if test_verify_otp(test_otp):
                print("\n[SUCCESS] OTP verified successfully!")
                
                # Step 4: Reset password
                if test_reset_password(test_otp):
                    print("\n[SUCCESS] Password reset successfully!")
                else:
                    print("\n[ERROR] Password reset failed")
            else:
                print("\n[ERROR] OTP verification failed")
        else:
            print("\n[ERROR] Invalid OTP format provided")
    
    print("\n" + "="*60)
    print("Testing Complete")
    print("="*60)
