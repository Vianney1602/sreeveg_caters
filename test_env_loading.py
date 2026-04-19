#!/usr/bin/env python3
"""Test environment variable loading"""
import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
print(f"Current Working Directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

# Load environment variables
load_dotenv('.env')

# Check if DATABASE_URL is loaded
db_url = os.environ.get("DATABASE_URL")
print(f"\nDATABASE_URL from os.environ: {db_url[:60] if db_url else 'NOT SET'}...")

# Now test Config class
from config import Config
print(f"\nFROM Config class:")
print(f"Config.DATABASE_URL: {Config.DATABASE_URL[:60] if Config.DATABASE_URL else 'NOT SET'}...")
print(f"Config.SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI[:60]}...")
