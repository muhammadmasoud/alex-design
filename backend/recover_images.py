#!/usr/bin/env python
"""
Recover images by linking optimized versions back to original database paths
This script will fix the broken image references in your database
"""
import os
import sys
import django
from pathlib import Path
from django.conf import settings

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service, ProjectImage, ServiceImage
import shutil

def recover_images():
    """Recover images by creating proper folder structure"""
    print("🚨 Starting image recovery...")
    
    # Create the missing directories
    media_root = settings.MEDIA_ROOT
    projects_dir = os.path.join(media_root, 'projects')
    services_dir = os.path.join(media_root, 'services')
    
    print(f"📁 Creating projects directory: {projects_dir}")
    os.makedirs(projects_dir, exist_ok=True)
    
    print(f"📁 Creating services directory: {services_dir}")
    os.makedirs(services_dir, exist_ok=True)
    
    # Create albums subdirectories
    projects_albums_dir = os.path.join(projects_dir, 'albums')
    services_albums_dir = os.path.join(services_dir, 'albums')
    
    os.makedirs(projects_albums_dir, exist_ok=True)
    os.makedirs(services_albums_dir, exist_ok=True)
    
    print("✅ Directories created successfully!")
    
    # Now copy optimized images back to original paths
    optimized_dir = os.path.join(media_root, 'optimized')
    
    if os.path.exists(optimized_dir):
        print("🔄 Copying optimized images back to original paths...")
        
        for filename in os.listdir(optimized_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                source_path = os.path.join(optimized_dir, filename)
                
                # Determine if it's a project or service image
                if 'album' in filename:
                    # Album image
                    if 'project' in filename or any(project_name in filename.lower() for project_name in ['jewelry', 'culture', 'villa', 'cafe', 'furniture', 'kitchen', 'hotel', 'office', 'vip', 'zenith']):
                        dest_path = os.path.join(projects_albums_dir, filename)
                    else:
                        dest_path = os.path.join(services_albums_dir, filename)
                else:
                    # Main image
                    if 'project' in filename or any(project_name in filename.lower() for project_name in ['jewelry', 'culture', 'villa', 'cafe', 'furniture', 'kitchen', 'hotel', 'office', 'vip', 'zenith']):
                        dest_path = os.path.join(projects_dir, filename)
                    else:
                        dest_path = os.path.join(services_dir, filename)
                
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"✅ Copied: {filename}")
                except Exception as e:
                    print(f"❌ Error copying {filename}: {e}")
    
    print("🎯 Image recovery complete!")
    print("🔍 Check your Django admin now - images should be visible!")

if __name__ == "__main__":
    try:
        recover_images()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
