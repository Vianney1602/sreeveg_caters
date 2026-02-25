#!/usr/bin/env python
"""
Test script for OTP flow with Redis retrieval
"""
import requests
import json
import time
import subprocess
import sys

BASE_URL = "http://localhost:8000/api/users"
TEST_EMAIL = "vianneyinfantraj1602@gmail.com"
TEST_PASSWORD = "TestPassword123!"
NEW_PASSWORD = "NewPassword456!"

def get_otp_from_redis():
    """Try to get OTP from Redis directly"""
    try:
        result = subprocess.run(
            ['redis-cli', 'get', f'otp:{TEST_EMAIL}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        otp = result.stdout.strip()
        if otp and otp != "(nil)" and len(otp) == 6 and otp.isdigit():
            return otp
    except Exception as e:
        print(f"[INFO] Could not retrieve OTP from Redis: {e}")
    return None

def test_forgot_password():
    """Test forgot-password endpoint"""
    print("\n[STEP 1] Testing forgot-password endpoint...")
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
    print(f"\n[STEP 2] Testing verify-otp endpoint with OTP: {otp}...")
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
    print(f"\n[STEP 3] Testing reset-password endpoint with OTP: {otp}...")
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
    print("="*70)
    print("OTP Flow Automated Testing")
    print("="*70)
    
    # Step 1: Request OTP
    if not test_forgot_password():
        print("\n[ERROR] forgot-password failed")
        sys.exit(1)
    
    print("\n[INFO] OTP request sent successfully!")
    print("[INFO] Waiting 2 seconds for OTP to be stored...")
    time.sleep(2)
    
    # Try to get OTP from Redis
    otp = get_otp_from_redis()
    
    if otp:
        print(f"\n[SUCCESS] Retrieved OTP from Redis: {otp}")
        
        # Verify OTP
        if test_verify_otp(otp):
            print("\n[SUCCESS] OTP verified successfully!")
            
            # Reset password
            if test_reset_password(otp):
                print("\n[SUCCESS] Password reset successfully!")
                print("\n" + "="*70)
                print("COMPLETE OTP FLOW TEST PASSED!")
                print("="*70)
            else:
                print("\n[ERROR] Password reset failed")
                sys.exit(1)
        else:
            print("\n[ERROR] OTP verification failed")
            sys.exit(1)
    else:
        print("\n[WARNING] Could not retrieve OTP from Redis")
        print("[INFO] This is OK if Redis is not running - fallback storage will be used")
        print("[INFO] Please check Flask console output for OTP code and run test manually")
        
        # Prompt for manual OTP entry
        manual_otp = input("\nEnter OTP from console (or press Enter to skip): ").strip()
        
        if manual_otp and len(manual_otp) == 6 and manual_otp.isdigit():
            if test_verify_otp(manual_otp):
                print("\n[SUCCESS] OTP verified!")
                if test_reset_password(manual_otp):
                    print("\n[SUCCESS] Password reset successfully!")
                    print("\n" + "="*70)
                    print("COMPLETE OTP FLOW TEST PASSED!")
                    print("="*70)
            else:
                print("\n[ERROR] OTP verification failed")
        else:
            print("\n[SKIPPED] Manual test skipped")
