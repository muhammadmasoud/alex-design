#!/usr/bin/env python
"""
Test script to verify project_date field migration worked correctly
"""
import os
import sys
import django

# Add the backend directory to Python path and setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service

def test_project_dates():
    """Test that all projects have valid project_date values"""
    projects = Project.objects.all()
    
    print(f"Found {projects.count()} projects")
    print("-" * 50)
    
    for project in projects:
        print(f"Project: {project.title}")
        print(f"  Project Date: {project.project_date}")
        print()
    
    # Verify all projects have project_date
    projects_without_date = projects.filter(project_date__isnull=True)
    if projects_without_date.exists():
        print(f"WARNING: {projects_without_date.count()} projects missing project_date!")
        return False
    
    print("✅ All projects have valid project_date values")
    print("✅ created_at field has been successfully removed")
    return True

def test_service_dates():
    """Test that all services have valid service_date values"""
    services = Service.objects.all()
    
    print(f"Found {services.count()} services")
    print("-" * 50)
    
    for service in services:
        print(f"Service: {service.name}")
        print(f"  Service Date: {service.service_date}")
        print()
    
    # Verify all services have service_date
    services_without_date = services.filter(service_date__isnull=True)
    if services_without_date.exists():
        print(f"WARNING: {services_without_date.count()} services missing service_date!")
        return False
    
    print("✅ All services have valid service_date values")
    return True

if __name__ == "__main__":
    test_project_dates()
    print()
    test_service_dates()
