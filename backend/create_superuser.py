#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import User

def create_superuser():
    email = "mohamedaboelhamd765@gmail.com"
    username = "aboelhamd"
    password = "LoE327|-E1v)"
    
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
