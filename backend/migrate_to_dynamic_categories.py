#!/usr/bin/env python
"""
Migration script to convert all legacy categories to dynamic categories
This script will:
1. Create dynamic categories/subcategories for all legacy data
2. Move all projects and services to use dynamic categories
3. Clean up legacy data
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import (
    Project, Service, 
    ProjectCategory, ProjectSubcategory, 
    ServiceCategory, ServiceSubcategory
)

def migrate_legacy_to_dynamic():
    """Migrate all legacy categories to dynamic categories"""
    
    print("=== MIGRATING LEGACY CATEGORIES TO DYNAMIC ===\n")
    
    # 1. Migrate Projects
    print("1. Migrating Projects...")
    projects_migrated = 0
    projects_with_legacy = Project.objects.filter(category__isnull=False).exclude(category='')
    
    for project in projects_with_legacy:
        if project.dynamic_category is None:  # Only migrate if not already using dynamic
            # Get or create the category
            category, created = ProjectCategory.objects.get_or_create(
                name=project.category,
                defaults={'description': f'Auto-migrated from legacy {project.category} category'}
            )
            if created:
                print(f"  Created category: {category.name}")
            
            # Set the dynamic category
            project.dynamic_category = category
            
            # Handle subcategory if it exists
            if project.subcategory and project.subcategory.strip():
                subcategory, created = ProjectSubcategory.objects.get_or_create(
                    name=project.subcategory,
                    category=category,
                    defaults={'description': f'Auto-migrated from legacy {project.subcategory} subcategory'}
                )
                if created:
                    print(f"    Created subcategory: {subcategory.name} under {category.name}")
                project.dynamic_subcategory = subcategory
            
            project.save()
            projects_migrated += 1
            print(f"  Migrated project: {project.title}")
    
    print(f"Projects migrated: {projects_migrated}\n")
    
    # 2. Migrate Services
    print("2. Migrating Services...")
    services_migrated = 0
    services_with_legacy = Service.objects.filter(category__isnull=False).exclude(category='')
    
    for service in services_with_legacy:
        if service.dynamic_category is None:  # Only migrate if not already using dynamic
            # Get or create the category
            category, created = ServiceCategory.objects.get_or_create(
                name=service.category,
                defaults={'description': f'Auto-migrated from legacy {service.category} category'}
            )
            if created:
                print(f"  Created category: {category.name}")
            
            # Set the dynamic category
            service.dynamic_category = category
            
            # Handle subcategory if it exists
            if service.subcategory and service.subcategory.strip():
                subcategory, created = ServiceSubcategory.objects.get_or_create(
                    name=service.subcategory,
                    category=category,
                    defaults={'description': f'Auto-migrated from legacy {service.subcategory} subcategory'}
                )
                if created:
                    print(f"    Created subcategory: {subcategory.name} under {category.name}")
                service.dynamic_subcategory = subcategory
            
            service.save()
            services_migrated += 1
            print(f"  Migrated service: {service.name}")
    
    print(f"Services migrated: {services_migrated}\n")
    
    # 3. Clear legacy fields after successful migration
    print("3. Clearing legacy category fields...")
    Project.objects.filter(dynamic_category__isnull=False).update(category=None, subcategory=None)
    Service.objects.filter(dynamic_category__isnull=False).update(category=None, subcategory=None)
    print("Legacy fields cleared!\n")
    
    # 4. Show final stats
    print("=== MIGRATION COMPLETE ===")
    print(f"Total Project Categories: {ProjectCategory.objects.count()}")
    print(f"Total Project Subcategories: {ProjectSubcategory.objects.count()}")
    print(f"Total Service Categories: {ServiceCategory.objects.count()}")
    print(f"Total Service Subcategories: {ServiceSubcategory.objects.count()}")
    
    print(f"\nProjects using dynamic categories: {Project.objects.filter(dynamic_category__isnull=False).count()}")
    print(f"Services using dynamic categories: {Service.objects.filter(dynamic_category__isnull=False).count()}")
    
    print(f"Projects still using legacy: {Project.objects.filter(category__isnull=False).exclude(category='').count()}")
    print(f"Services still using legacy: {Service.objects.filter(category__isnull=False).exclude(category='').count()}")

if __name__ == "__main__":
    migrate_legacy_to_dynamic()
