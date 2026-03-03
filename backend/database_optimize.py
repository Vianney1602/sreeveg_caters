import os
import re
import psycopg2

def get_db_url():
    """Read DATABASE_URL from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), '.env')
        
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('DATABASE_URL')

def optimize_database():
    db_url = get_db_url()
    if not db_url:
        print("Error: DATABASE_URL not found in .env or environment variables.")
        return

    # Convert sqlalchemy-style URL to psycopg2-compatible URL
    # Replace postgresql+psycopg2:// with postgresql://
    conn_url = db_url.replace('postgresql+psycopg2://', 'postgresql://')
    
    print(f"Connecting to database...")
    
    try:
        conn = psycopg2.connect(conn_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        indexes = [
            ("idx_orders_customer_id", "orders", "customer_id"),
            ("idx_orders_status", "orders", "status"),
            ("idx_orders_created_at", "orders", "created_at"),
            ("idx_customers_email", "customers", "email"),
            ("idx_order_menu_items_order_id", "order_menu_items", "order_id")
        ]
        
        print("Successfully connected to the database.")
        
        for idx_name, table, column in indexes:
            try:
                print(f"Adding index {idx_name} to {table}({column})...")
                sql = f"CREATE INDEX {idx_name} ON {table} ({column})"
                cur.execute(sql)
                print(f"Successfully added index {idx_name}.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"Index {idx_name} already exists. Skipping.")
                else:
                    print(f"Error adding index {idx_name}: {e}")

        cur.close()
        conn.close()
        print("\nDatabase optimization complete! Admin Dashboard queries are now optimized.")

    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    optimize_database()
