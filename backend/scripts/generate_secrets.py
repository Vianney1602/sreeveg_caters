#!/usr/bin/env python3
"""
Generate secure secrets for JWT and Flask application.
Creates a .env file with random secrets if one doesn't exist.
"""
import secrets
import string
import os
from pathlib import Path


def generate_secure_secret(length=32):
    """Generate a cryptographically secure random string."""
    return secrets.token_urlsafe(length)


def generate_password(length=16):
    """Generate a strong random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    # Ensure it has at least one uppercase, lowercase, digit, and special char
    if (any(c.isupper() for c in password) and 
        any(c.islower() for c in password) and 
        any(c.isdigit() for c in password) and
        any(c in "!@#$%^&*" for c in password)):
        return password
    # If not, try again
    return generate_password(length)


def main():
    """Generate and save secrets to .env file."""
    # Get backend directory
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / '.env'
    env_example_file = backend_dir / '.env.example'
    
    # Check if .env already exists
    if env_file.exists():
        response = input(f"\n⚠️  {env_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted. Existing .env file was not modified.")
            return
    
    # Generate secrets
    print("\n🔐 Generating secure secrets...")
    jwt_secret = generate_secure_secret(32)
    flask_secret = generate_secure_secret(32)
    admin_password = generate_password(16)
    
    # Create .env content
    env_content = f"""# Flask Configuration
SECRET_KEY={flask_secret}

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}
JWT_ACCESS_TOKEN_EXPIRES=7200

# Admin Credentials (CHANGE THESE!)
ADMIN_USERNAME=admin@shanmugabhavaan.com
ADMIN_PASSWORD={admin_password}

# Database
# SQLALCHEMY_DATABASE_URI=sqlite:///database.db

# Optional: Razorpay Keys (for payment integration)
# RAZORPAY_KEY_ID=your_razorpay_key_id
# RAZORPAY_KEY_SECRET=your_razorpay_key_secret
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print("\n📋 Generated credentials:")
    print(f"   Admin Username: admin@yourdomain.com")
    print(f"   Admin Password: {admin_password}")
    print(f"\n⚠️  IMPORTANT: Change ADMIN_USERNAME in {env_file} to your actual email!")
    print(f"⚠️  Store these credentials securely and don't commit .env to git!")
    
    # Create .env.example if it doesn't exist
    if not env_example_file.exists():
        example_content = """# Flask Configuration
SECRET_KEY=your_secret_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ACCESS_TOKEN_EXPIRES=7200

# Admin Credentials
ADMIN_USERNAME=admin@yourdomain.com
ADMIN_PASSWORD=your_secure_password_here

# Database (optional - defaults to sqlite:///database.db)
# SQLALCHEMY_DATABASE_URI=sqlite:///database.db

# Optional: Razorpay Keys (for payment integration)
# RAZORPAY_KEY_ID=your_razorpay_key_id
# RAZORPAY_KEY_SECRET=your_razorpay_key_secret
"""
        with open(env_example_file, 'w') as f:
            f.write(example_content)
        print(f"✅ Created {env_example_file}")
    
    # Check if .gitignore exists and has .env
    gitignore_file = backend_dir.parent / '.gitignore'
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
        if '.env' not in gitignore_content:
            print("\n⚠️  WARNING: .env is not in .gitignore!")
            print("   Add '.env' to your .gitignore to prevent committing secrets.")
    else:
        print("\n⚠️  No .gitignore found. Consider creating one with '.env' entry.")


if __name__ == '__main__':
    main()
