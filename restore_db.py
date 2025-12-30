#!/usr/bin/env python
"""Restore PostgreSQL backup to Render database"""

import subprocess
import sys

def restore_database():
    """Restore the cater_db backup to Render"""
    try:
        print("Starting database restore to Render...")
        
        # Internal URL for same-region connection
        render_url = "postgresql://sreeveg_caters_user:pvnKhZ99nOZaMduJ1cu31PZY0V20QXkq@dpg-d59er6mr433s73fqbqpg-a/sreeveg_caters"
        backup_file = r'h:\cater-main\cater_backup.sql'
        
        print(f"Restore from: {backup_file}")
        print(f"Restore to: Render PostgreSQL")
        
        # Read backup file
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Restore using psql
        cmd = [
            r'C:\Program Files\PostgreSQL\18\bin\psql.exe',
            '-v', 'ON_ERROR_STOP=1',
            render_url
        ]
        
        result = subprocess.run(cmd, input=backup_content, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ERROR during restore:\n{result.stderr}")
            return False
        
        print("\nSUCCESS - Database restored to Render!")
        print("Output:")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    success = restore_database()
    sys.exit(0 if success else 1)
