#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from portfolio.models import Project, Service

def update_orders():
    print("Updating existing project and service orders...")
    
    # Update projects with order = 0 to have sequential orders
    projects_without_order = Project.objects.filter(order=0).order_by('-project_date')
    max_order = Project.objects.exclude(order=0).aggregate(models.Max('order'))['order__max'] or 0
    
    for i, project in enumerate(projects_without_order, start=max_order + 1):
        project.order = i
        project.save()
        print(f"Updated project '{project.title}' to order {i}")
    
    # Update services with order = 0 to have sequential orders
    services_without_order = Service.objects.filter(order=0).order_by('name')
    max_order = Service.objects.exclude(order=0).aggregate(models.Max('order'))['order__max'] or 0
    
    for i, service in enumerate(services_without_order, start=max_order + 1):
        service.order = i
        service.save()
        print(f"Updated service '{service.name}' to order {i}")
    
    print("Orders updated successfully!")

if __name__ == '__main__':
    from django.db import models
    update_orders()
