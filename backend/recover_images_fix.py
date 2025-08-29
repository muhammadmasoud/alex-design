#!/usr/bin/env python
"""
FIXED: Recover ALL images by copying optimized versions to both projects and services folders
This script will restore ALL your images by putting them in the right places
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

def recover_all_images():
    """Recover ALL images by copying them to the right folders"""
    print("🚨 Starting COMPLETE image recovery...")
    
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
    
    # Now copy ALL optimized images to BOTH locations
    optimized_dir = os.path.join(media_root, 'optimized')
    
    if os.path.exists(optimized_dir):
        print("🔄 Copying ALL optimized images to restore folder structure...")
        
        total_images = 0
        copied_images = 0
        
        for filename in os.listdir(optimized_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                total_images += 1
                source_path = os.path.join(optimized_dir, filename)
                
                # Copy to BOTH locations to ensure all images are restored
                if 'album' in filename:
                    # Album image - copy to both albums folders
                    dest1 = os.path.join(projects_albums_dir, filename)
                    dest2 = os.path.join(services_albums_dir, filename)
                    
                    try:
                        shutil.copy2(source_path, dest1)
                        shutil.copy2(source_path, dest2)
                        copied_images += 1
                        print(f"✅ Copied album: {filename}")
                    except Exception as e:
                        print(f"❌ Error copying {filename}: {e}")
                else:
                    # Main image - copy to both main folders
                    dest1 = os.path.join(projects_dir, filename)
                    dest2 = os.path.join(services_dir, filename)
                    
                    try:
                        shutil.copy2(source_path, dest1)
                        shutil.copy2(source_path, dest2)
                        copied_images += 1
                        print(f"✅ Copied main: {filename}")
                    except Exception as e:
                        print(f"❌ Error copying {filename}: {e}")
        
        print(f"🎯 Recovery complete! Copied {copied_images}/{total_images} images")
        
        # Also copy from webp folder if it exists
        webp_dir = os.path.join(media_root, 'webp')
        if os.path.exists(webp_dir):
            print("🔄 Also copying WebP images...")
            for filename in os.listdir(webp_dir):
                if filename.endswith('.webp'):
                    source_path = os.path.join(webp_dir, filename)
                    
                    # Copy to both locations
                    if 'album' in filename:
                        dest1 = os.path.join(projects_albums_dir, filename)
                        dest2 = os.path.join(services_albums_dir, filename)
                    else:
                        dest1 = os.path.join(projects_dir, filename)
                        dest2 = os.path.join(services_dir, filename)
                    
                    try:
                        shutil.copy2(source_path, dest1)
                        shutil.copy2(source_path, dest2)
                        print(f"✅ Copied WebP: {filename}")
                    except Exception as e:
                        print(f"❌ Error copying WebP {filename}: {e}")
    
    print("🎯 COMPLETE image recovery finished!")
    print("🔍 Check your Django admin now - ALL images should be visible!")
    
    # Show what we have now
    print("\n📊 Current folder contents:")
    if os.path.exists(projects_dir):
        project_files = len([f for f in os.listdir(projects_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Projects: {project_files} images")
    
    if os.path.exists(projects_albums_dir):
        project_album_files = len([f for f in os.listdir(projects_albums_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Project Albums: {project_album_files} images")
    
    if os.path.exists(services_dir):
        service_files = len([f for f in os.listdir(services_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Services: {service_files} images")
    
    if os.path.exists(services_albums_dir):
        service_album_files = len([f for f in os.listdir(services_albums_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Service Albums: {service_album_files} images")

if __name__ == "__main__":
    try:
        recover_all_images()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
