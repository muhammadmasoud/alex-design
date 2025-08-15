#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import User

def create_superuser():
    # Load credentials from environment variables for security
    email = os.environ.get("ADMIN_EMAIL")
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")
    if not all([email, username, password]):
        raise ValueError("Admin credentials not set in environment variables.")
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"User with email {email} already exists!")
        user = User.objects.get(email=email)
        # Update password and superuser status
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Updated existing user {username} to superuser status!")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser {username} created successfully!")
    
    return user

if __name__ == "__main__":
    create_superuser()
