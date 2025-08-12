#!/usr/bin/env python3
"""
Script to update existing services with sample prices
Run this after adding the price field to set some example prices
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Service

def update_service_prices():
    """Update existing services with sample prices"""
    
    # Sample price ranges for different types of services
    price_suggestions = {
        'architectural design': 2500.00,
        'interior design': 1500.00,
        '3d visualization': 800.00,
        'consultation': 300.00,
        'planning': 1200.00,
        'renovation': 2000.00,
        'landscaping': 1800.00,
        'project management': 2200.00,
    }
    
    services = Service.objects.all()
    
    if not services.exists():
        print("No services found in the database.")
        return
    
    print(f"Found {services.count()} services. Updating prices...")
    
    updated_count = 0
    
    for service in services:
        # Skip services that already have a non-zero price
        if service.price > 0:
            print(f"Service '{service.name}' already has a price: ${service.price}")
            continue
            
        # Try to match service name with price suggestions
        service_name_lower = service.name.lower()
        suggested_price = None
        
        for keyword, price in price_suggestions.items():
            if keyword in service_name_lower:
                suggested_price = price
                break
        
        # If no match found, use a default price based on service type
        if suggested_price is None:
            if 'design' in service_name_lower:
                suggested_price = 2000.00
            elif 'visualization' in service_name_lower or '3d' in service_name_lower:
                suggested_price = 800.00
            elif 'consultation' in service_name_lower or 'consulting' in service_name_lower:
                suggested_price = 400.00
            else:
                suggested_price = 1500.00  # Default price
        
        # Update the service
        service.price = suggested_price
        service.save()
        
        print(f"Updated '{service.name}' with price: ${suggested_price}")
        updated_count += 1
    
    print(f"\nSuccessfully updated {updated_count} services with prices.")
    
    # Display all services with their prices
    print("\nCurrent services and prices:")
    print("-" * 50)
    for service in Service.objects.all():
        print(f"{service.name}: ${service.price}")

if __name__ == '__main__':
    update_service_prices()
