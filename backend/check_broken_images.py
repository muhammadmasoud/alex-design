#!/usr/bin/env python3
"""
Check what's wrong with the images after optimization
"""
import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service

def check_image_issues():
    print("=== CHECKING IMAGE ISSUES ===")
    
    print("\n=== PROJECT IMAGES ===")
    broken_projects = []
    for p in Project.objects.all():
        if p.image:
            image_path = f"media/{p.image.name}"
            exists = os.path.exists(image_path)
            print(f"{p.title}: {p.image.name} - {'✅ EXISTS' if exists else '❌ MISSING'}")
            if not exists:
                broken_projects.append(p)
        else:
            print(f"{p.title}: No image")
    
    print("\n=== SERVICE IMAGES ===")
    broken_services = []
    for s in Service.objects.all():
        if s.icon:
            icon_path = f"media/{s.icon.name}"
            exists = os.path.exists(icon_path)
            print(f"{s.name}: {s.icon.name} - {'✅ EXISTS' if exists else '❌ MISSING'}")
            if not exists:
                broken_services.append(s)
        else:
            print(f"{s.name}: No icon")
    
    print(f"\n=== SUMMARY ===")
    print(f"Broken projects: {len(broken_projects)}")
    print(f"Broken services: {len(broken_services)}")
    
    if broken_projects or broken_services:
        print(f"\n=== AVAILABLE FILES ===")
        print("Projects folder:")
        for file in os.listdir("media/projects"):
            if not os.path.isdir(f"media/projects/{file}"):
                print(f"  {file}")
        
        print("\nServices folder:")
        for file in os.listdir("media/services"):
            if not os.path.isdir(f"media/services/{file}"):
                print(f"  {file}")

if __name__ == '__main__':
    check_image_issues()
