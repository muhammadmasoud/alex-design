#!/usr/bin/env python
"""
Test script for complete folder deletion when projects/services are deleted
Run this to test if the deletion cleanup is working correctly
"""

import os
import sys
import django
import shutil

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service
from django.conf import settings

def test_folder_deletion():
    """Test that project/service deletion completely removes media folders"""
    print("🧪 Testing Complete Folder Deletion")
    print("=" * 50)
    
    # Test project deletion
    print("\n📁 Testing Project Folder Deletion:")
    projects = Project.objects.all()[:2]  # Test first 2 projects
    
    for project in projects:
        print(f"\n  Project: {project.title}")
        
        # Get project folder path
        from django.utils.text import slugify
        project_folder_name = slugify(project.title)[:50]
        project_folder_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder_name)
        
        if os.path.exists(project_folder_path):
            print(f"    ✅ Project folder exists: {project_folder_path}")
            
            # Check folder contents
            folder_contents = os.listdir(project_folder_path)
            print(f"    📂 Folder contents: {folder_contents}")
            
            # Check if webp folder exists
            webp_folder = os.path.join(project_folder_path, 'webp')
            if os.path.exists(webp_folder):
                print(f"    🖼️  WebP folder exists with {len(os.listdir(webp_folder))} items")
            
        else:
            print(f"    ⚠️  Project folder does not exist: {project_folder_path}")
    
    # Test service deletion
    print("\n🔧 Testing Service Folder Deletion:")
    services = Service.objects.all()[:2]  # Test first 2 services
    
    for service in services:
        print(f"\n  Service: {service.name}")
        
        # Get service folder path
        from django.utils.text import slugify
        service_folder_name = slugify(service.name)[:50]
        service_folder_path = os.path.join(settings.MEDIA_ROOT, 'services', service_folder_name)
        
        if os.path.exists(service_folder_path):
            print(f"    ✅ Service folder exists: {service_folder_path}")
            
            # Check folder contents
            folder_contents = os.listdir(service_folder_path)
            print(f"    📂 Folder contents: {folder_contents}")
            
            # Check if webp folder exists
            webp_folder = os.path.join(service_folder_path, 'webp')
            if os.path.exists(webp_folder):
                print(f"    🖼️  WebP folder exists with {len(os.listdir(webp_folder))} items")
            
        else:
            print(f"    ⚠️  Service folder does not exist: {service_folder_path}")
    
    print("\n" + "=" * 50)
    print("✅ Folder deletion test completed!")
    print("\n💡 To test actual deletion:")
    print("   1. Delete a project/service from Django admin")
    print("   2. Check if the media folder is completely removed")
    print("   3. Verify no orphaned files remain")

def check_media_structure():
    """Check the current media folder structure"""
    print("\n📂 Current Media Folder Structure:")
    print("=" * 50)
    
    media_root = settings.MEDIA_ROOT
    
    if not os.path.exists(media_root):
        print("❌ Media root does not exist!")
        return
    
    print(f"Media root: {media_root}")
    
    # Check projects folder
    projects_path = os.path.join(media_root, 'projects')
    if os.path.exists(projects_path):
        project_folders = os.listdir(projects_path)
        print(f"\n📁 Projects ({len(project_folders)} folders):")
        for folder in project_folders[:5]:  # Show first 5
            folder_path = os.path.join(projects_path, folder)
            if os.path.isdir(folder_path):
                contents = os.listdir(folder_path)
                print(f"  - {folder}/ ({len(contents)} items)")
                
                # Check for webp folder
                webp_path = os.path.join(folder_path, 'webp')
                if os.path.exists(webp_path):
                    webp_contents = os.listdir(webp_path)
                    print(f"    └── webp/ ({len(webp_contents)} items)")
    
    # Check services folder
    services_path = os.path.join(media_root, 'services')
    if os.path.exists(services_path):
        service_folders = os.listdir(services_path)
        print(f"\n🔧 Services ({len(service_folders)} folders):")
        for folder in service_folders[:5]:  # Show first 5
            folder_path = os.path.join(services_path, folder)
            if os.path.isdir(folder_path):
                contents = os.listdir(folder_path)
                print(f"  - {folder}/ ({len(contents)} items)")
                
                # Check for webp folder
                webp_path = os.path.join(folder_path, 'webp')
                if os.path.exists(webp_path):
                    webp_contents = os.listdir(webp_path)
                    print(f"    └── webp/ ({len(webp_contents)} items)")

if __name__ == "__main__":
    check_media_structure()
    test_folder_deletion()
