#!/usr/bin/env python3
"""
Quick test: Create a demo user account in the database
so you can sign in without Google OAuth
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import sys

# Import models properly
sys.path.insert(0, 'backend')
from extensions import db as db_ext
from models import Customer

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not set in .env")
    sys.exit(1)

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Demo account
DEMO_EMAIL = "demo@hotelshanmugabhavaan.com"
DEMO_PASSWORD = "Demo@123"

try:
    # Check if demo user already exists
    existing = session.query(Customer).filter_by(email=DEMO_EMAIL).first()
    if existing:
        print(f"✅ Demo user already exists: {DEMO_EMAIL}")
        print(f"   Password: {DEMO_PASSWORD}")
    else:
        # Create demo user with correct field names
        demo_user = Customer(
            full_name="Demo User",
            email=DEMO_EMAIL,
            phone_number="9999999999",
            password_hash=generate_password_hash(DEMO_PASSWORD)
        )
        session.add(demo_user)
        session.commit()
        print(f"✅ Demo user created successfully!")
        print(f"   Email: {DEMO_EMAIL}")
        print(f"   Password: {DEMO_PASSWORD}")
        print(f"\nℹ️ Sign in instructions:")
        print(f"   1. Go to http://127.0.0.1:3000/signin")
        print(f"   2. Click 'Create an account' to sign up, OR")
        print(f"   3. Use email/password to sign in (if Google OAuth fails)")
except Exception as e:
    print(f"❌ Error creating demo user: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()

