#!/usr/bin/env python
"""Backup PostgreSQL cater_db database"""

import subprocess
import os
import sys

def backup_database():
    """Backup the cater_db database"""
    try:
        print("Starting database backup...")
        print("Database: cater_db")
        print("Host: localhost")
        print("User: postgres")
        
        # Run pg_dump
        cmd = [
            r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe',
            '-U', 'postgres',
            '-h', 'localhost',
            '-d', 'cater_db',
            '--format=plain',
            '--verbose'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            return False
        
        # Save backup
        backup_file = r'h:\cater-main\cater_backup.sql'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        size = os.path.getsize(backup_file)
        print(f"\nSUCCESS - Backup completed!")
        print(f"File: {backup_file}")
        print(f"Size: {size} bytes ({size/1024:.2f} KB)")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    success = backup_database()
    sys.exit(0 if success else 1)
