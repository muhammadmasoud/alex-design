#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory
from portfolio.constants import PROJECT_CATEGORIES, SERVICE_CATEGORIES

def populate_categories():
    print("Populating categories from constants...")
    
    # Populate Project Categories
    print("\n--- Populating Project Categories ---")
    for category_name, subcategories in PROJECT_CATEGORIES.items():
        category, created = ProjectCategory.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Category for {category_name} projects'}
        )
        if created:
            print(f"Created project category: {category_name}")
        else:
            print(f"Project category already exists: {category_name}")
        
        # Populate subcategories
        for subcat_value, subcat_label in subcategories:
            subcategory, created = ProjectSubcategory.objects.get_or_create(
                name=subcat_label,
                category=category,
                defaults={'description': f'Subcategory for {subcat_label}'}
            )
            if created:
                print(f"  Created subcategory: {subcat_label}")
    
    # Populate Service Categories
    print("\n--- Populating Service Categories ---")
    for category_name, subcategories in SERVICE_CATEGORIES.items():
        category, created = ServiceCategory.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Category for {category_name} services'}
        )
        if created:
            print(f"Created service category: {category_name}")
        else:
            print(f"Service category already exists: {category_name}")
        
        # Populate subcategories
        for subcat_value, subcat_label in subcategories:
            subcategory, created = ServiceSubcategory.objects.get_or_create(
                name=subcat_label,
                category=category,
                defaults={'description': f'Subcategory for {subcat_label}'}
            )
            if created:
                print(f"  Created subcategory: {subcat_label}")
    
    print(f"\nSummary:")
    print(f"Project Categories: {ProjectCategory.objects.count()}")
    print(f"Project Subcategories: {ProjectSubcategory.objects.count()}")
    print(f"Service Categories: {ServiceCategory.objects.count()}")
    print(f"Service Subcategories: {ServiceSubcategory.objects.count()}")

if __name__ == "__main__":
    populate_categories()
