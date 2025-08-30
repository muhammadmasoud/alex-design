#!/usr/bin/env python
"""
Test script to demonstrate folder deletion when projects are deleted
This script shows how the automatic folder cleanup works
"""

import os
import sys
import django
import shutil
import time

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service
from portfolio.image_optimizer import ImageOptimizer
from django.conf import settings

def demonstrate_folder_deletion():
    """Demonstrate how folder deletion works"""
    print("🧪 Demonstrating Folder Deletion Functionality")
    print("=" * 60)
    
    # Get existing projects
    projects = Project.objects.all()
    if not projects.exists():
        print("❌ No projects found in database!")
        return
    
    project = projects.first()
    print(f"\n📁 Found project: {project.title}")
    
    # Get project folder path
    project_folder = ImageOptimizer._get_project_folder(project)
    print(f"📍 Project folder path: {project_folder}")
    
    # Check if folder exists
    if os.path.exists(project_folder):
        print(f"✅ Project folder exists")
        
        # Show folder contents
        print("\n📂 Current folder contents:")
        for root, dirs, files in os.walk(project_folder):
            level = root.replace(project_folder, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Test the deletion method (but don't actually delete)
        print(f"\n🔍 Testing deletion method (simulation only):")
        print(f"   Method: ImageOptimizer.delete_project_folder(project)")
        print(f"   This would delete: {project_folder}")
        print(f"   And all its contents recursively")
        
        # Show what would happen
        print(f"\n💡 When you delete this project from Django admin:")
        print(f"   1. Django calls the post_delete signal")
        print(f"   2. Signal calls ImageOptimizer.delete_project_folder()")
        print(f"   3. Method deletes entire folder: {project_folder}")
        print(f"   4. All files and subfolders are removed")
        print(f"   5. No orphaned files remain")
        
    else:
        print(f"⚠️  Project folder does not exist")
    
    print("\n" + "=" * 60)
    print("✅ Demonstration completed!")
    print("\n🚀 To test actual deletion:")
    print("   1. Go to Django admin: http://localhost:8000/admin/")
    print("   2. Find the project: {project.title}")
    print("   3. Delete it")
    print("   4. Check that the folder is completely removed")
    print("   5. Verify no orphaned files remain in media/projects/")

def check_signal_registration():
    """Check if the delete signals are properly registered"""
    print("\n🔌 Checking Signal Registration")
    print("=" * 40)
    
    try:
        from django.db.models.signals import post_delete
        from django.dispatch import receiver
        from portfolio.signals import cleanup_project_images_on_delete, cleanup_service_images_on_delete
        
        # Check if signals are connected
        receivers = post_delete._live_receivers(sender=Project)
        project_signal_connected = any(
            hasattr(receiver, '__name__') and receiver.__name__ == 'cleanup_project_images_on_delete' 
            for receiver in receivers
        )
        
        receivers = post_delete._live_receivers(sender=Service)
        service_signal_connected = any(
            hasattr(receiver, '__name__') and receiver.__name__ == 'cleanup_service_images_on_delete' 
            for receiver in receivers
        )
        
        print(f"📡 Project delete signal: {'✅ Connected' if project_signal_connected else '❌ Not connected'}")
        print(f"📡 Service delete signal: {'✅ Connected' if service_signal_connected else '❌ Not connected'}")
        
        if project_signal_connected and service_signal_connected:
            print("\n🎉 All signals are properly registered!")
        else:
            print("\n⚠️  Some signals are not connected. Check your apps.py configuration.")
            
    except Exception as e:
        print(f"❌ Error checking signals: {str(e)}")

def show_media_structure():
    """Show the current media folder structure"""
    print("\n📂 Current Media Structure")
    print("=" * 40)
    
    media_root = settings.MEDIA_ROOT
    projects_path = os.path.join(media_root, 'projects')
    
    if os.path.exists(projects_path):
        project_folders = [d for d in os.listdir(projects_path) if os.path.isdir(os.path.join(projects_path, d))]
        print(f"📁 Projects folder: {projects_path}")
        print(f"   Contains {len(project_folders)} project folders:")
        
        for folder in project_folders:
            folder_path = os.path.join(projects_path, folder)
            contents = os.listdir(folder_path)
            print(f"   - {folder}/ ({len(contents)} items)")
            
            # Show webp folder if it exists
            webp_path = os.path.join(folder_path, 'webp')
            if os.path.exists(webp_path):
                webp_contents = os.listdir(webp_path)
                print(f"     └── webp/ ({len(webp_contents)} optimized images)")
    else:
        print(f"❌ Projects folder does not exist: {projects_path}")

if __name__ == "__main__":
    show_media_structure()
    check_signal_registration()
    demonstrate_folder_deletion()
