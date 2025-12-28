"""
Setup PostgreSQL Database for Cater Application
Creates the cater_db database and migrates data from SQLite
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the PostgreSQL database"""
    print("\n" + "=" * 70)
    print("SETTING UP POSTGRESQL DATABASE")
    print("=" * 70)
    
    # Parse the DATABASE_URL
    db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:Admin%40123@localhost:5432/cater_db")
    print(f"\n📍 Database URL: {db_url}")
    
    # Parse connection details
    try:
        # postgresql://postgres:Admin%40123@localhost:5432/cater_db
        parts = db_url.replace("postgresql://", "").split("@")
        credentials = parts[0].split(":")
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        username = credentials[0]
        password = credentials[1]
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        db_name = host_port_db[1]
        
        # URL decode the password
        password = password.replace("%40", "@")
        
        print(f"   User: {username}")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {db_name}")
        
    except Exception as e:
        print(f"\n❌ Error parsing DATABASE_URL: {e}")
        print("   Make sure DATABASE_URL is set correctly in .env")
        return False
    
    # Connect to default postgres database to create our database
    try:
        print(f"\n🔌 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database="postgres"  # Connect to default postgres DB first
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{db_name}' already exists!")
        else:
            print(f"📝 Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection error: {e}")
        print("\n📋 Make sure:")
        print("   1. PostgreSQL is installed and running")
        print("   2. The credentials in .env are correct")
        print("   3. Run: 'pg_ctl -D 'C:\\Program Files\\PostgreSQL\\16\\data' start' (or your PostgreSQL version)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    if success:
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print("\n📋 Next: Run the migration script")
        print("   python scripts/migrate_sqlite_to_pg.py")
        sys.exit(0)
    else:
        sys.exit(1)
