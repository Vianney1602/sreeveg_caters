"""
E2E test for admin password reset flow.
Uses Flask test client - no external server required.
Run from backend folder:
    python test_e2e_admin_reset.py
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

print("\n" + "="*60)
print("ADMIN PASSWORD RESET - E2E TEST (Flask Test Client)")
print("="*60 + "\n")

# ---- Setup ----------------------------------------------------
from app import create_app, db
from api.users import otp_storage   # in-memory fallback dict
from models import AdminSettings

app = create_app()
client = app.test_client()
NEW_PASSWORD = "NewAdmin@2026"

# ---- Step 1: forgot-password ----------------------------------
print("STEP 1: POST /api/users/admin/forgot-password")
resp = client.post(
    "/api/users/admin/forgot-password",
    content_type="application/json",
    data=json.dumps({})
)
body = json.loads(resp.data)
print(f"  Status: {resp.status_code}")
print(f"  Body:   {body}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {body}"

# Grab OTP from in-memory storage (works when Redis is down)
from config import Config
admin_key = f"admin:{Config.ADMIN_EMAIL}"
assert admin_key in otp_storage, f"OTP not found in otp_storage under key '{admin_key}'"
otp = otp_storage[admin_key]["otp"]
print(f"  OTP captured from storage: {otp}")
print("  [PASS]")

# ---- Step 2: verify-otp ---------------------------------------
print("\nSTEP 2: POST /api/users/admin/verify-otp")
resp = client.post(
    "/api/users/admin/verify-otp",
    content_type="application/json",
    data=json.dumps({"otp": otp})
)
body = json.loads(resp.data)
print(f"  Status: {resp.status_code}")
print(f"  Body:   {body}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {body}"
print("  [PASS]")

# ---- Step 3: reset-password -----------------------------------
print("\nSTEP 3: POST /api/users/admin/reset-password")
resp = client.post(
    "/api/users/admin/reset-password",
    content_type="application/json",
    data=json.dumps({"otp": otp, "new_password": NEW_PASSWORD})
)
body = json.loads(resp.data)
print(f"  Status: {resp.status_code}")
print(f"  Body:   {body}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {body}"
print("  [PASS]")

# ---- Step 4: verify DB row ------------------------------------
print("\nSTEP 4: Verify admin_settings row in DB")
with app.app_context():
    row = AdminSettings.query.filter_by(admin_id=1).first()
    if row:
        print(f"  admin_id:    {row.admin_id}")
        print(f"  email:       {row.email}")
        print(f"  hash_length: {len(row.password_hash) if row.password_hash else 0}")
        print(f"  updated_at:  {row.updated_at}")
        assert row.password_hash, "password_hash is empty!"
        print("  [PASS] - Password hash stored in DB")
    else:
        print("  [FAIL] - No row found in admin_settings!")
        sys.exit(1)

# ---- Step 5: login with new password -------------------------
print("\nSTEP 5: POST /api/users/login with new password")
resp = client.post(
    "/api/users/login",
    content_type="application/json",
    data=json.dumps({"email": Config.ADMIN_EMAIL, "password": NEW_PASSWORD})
)
body = json.loads(resp.data)
print(f"  Status: {resp.status_code}")
is_admin = body.get("isAdmin", False)
has_token = bool(body.get("token"))
print(f"  isAdmin: {is_admin}")
print(f"  hasToken: {has_token}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {body}"
assert is_admin, "isAdmin should be True"
assert has_token, "No token returned"
print("  [PASS] - Admin login with new password works!")

# ---- Summary -------------------------------------------------
print("\n" + "="*60)
print("ALL 5 STEPS PASSED - E2E Test Complete!")
print("="*60)
print(f"\nNew admin password '{NEW_PASSWORD}' is now active in Neon DB.")
print("The admin_settings table has a hashed password stored.")
print("Login with the new password works end-to-end.")
