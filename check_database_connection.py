#!/usr/bin/env python3
"""Check database connection and tables"""
import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

from sqlalchemy import inspect, text
from app import create_app, db

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("DATABASE CONNECTION CHECK")
    print("="*70)
    
    # Get database URL
    db_url = os.environ.get("DATABASE_URL", "Not set")
    print(f"\nDatabase URL: {db_url[:50]}...")
    
    # Get inspector
    inspector = inspect(db.engine)
    
    # List all tables
    tables = inspector.get_table_names()
    print(f"\nTotal tables in database: {len(tables)}")
    print("\nTables:")
    for table in tables:
        print(f"  - {table}")
        
        # Get row count for each table
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"    └─ Row count: {count}")
        except:
            print(f"    └─ (unable to count)")
    
    print("\n" + "="*70)
