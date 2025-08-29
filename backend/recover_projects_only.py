#!/usr/bin/env python
"""
RECOVER PROJECTS ONLY: Restore all 28-29 projects with 223 images
This script will ONLY recover project images, not services
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

from portfolio.models import Project, ProjectImage
import shutil

def recover_projects_only():
    """Recover ONLY project images - no services"""
    print("🚨 Starting PROJECT-ONLY recovery...")
    print("🎯 Target: 28-29 projects with 223 images")
    
    # Create ONLY the projects directory
    media_root = settings.MEDIA_ROOT
    projects_dir = os.path.join(media_root, 'projects')
    projects_albums_dir = os.path.join(projects_dir, 'albums')
    
    print(f"📁 Creating projects directory: {projects_dir}")
    os.makedirs(projects_dir, exist_ok=True)
    
    print(f"📁 Creating projects albums directory: {projects_albums_dir}")
    os.makedirs(projects_albums_dir, exist_ok=True)
    
    print("✅ Project directories created successfully!")
    
    # Copy ALL images from optimized folder to projects
    optimized_dir = os.path.join(media_root, 'optimized')
    
    if os.path.exists(optimized_dir):
        print("🔄 Copying ALL optimized images to projects folder...")
        
        total_images = 0
        copied_images = 0
        
        for filename in os.listdir(optimized_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                total_images += 1
                source_path = os.path.join(optimized_dir, filename)
                
                # ALL images go to projects (since you have 0 services)
                if 'album' in filename:
                    # Album image goes to projects/albums
                    dest_path = os.path.join(projects_albums_dir, filename)
                else:
                    # Main image goes to projects
                    dest_path = os.path.join(projects_dir, filename)
                
                try:
                    shutil.copy2(source_path, dest_path)
                    copied_images += 1
                    print(f"✅ Copied: {filename}")
                except Exception as e:
                    print(f"❌ Error copying {filename}: {e}")
        
        print(f"🎯 Recovery complete! Copied {copied_images}/{total_images} images")
        
        # Also copy from webp folder
        webp_dir = os.path.join(media_root, 'webp')
        if os.path.exists(webp_dir):
            print("🔄 Also copying WebP images to projects...")
            webp_count = 0
            for filename in os.listdir(webp_dir):
                if filename.endswith('.webp'):
                    source_path = os.path.join(webp_dir, filename)
                    
                    if 'album' in filename:
                        dest_path = os.path.join(projects_albums_dir, filename)
                    else:
                        dest_path = os.path.join(projects_dir, filename)
                    
                    try:
                        shutil.copy2(source_path, dest_path)
                        webp_count += 1
                        print(f"✅ Copied WebP: {filename}")
                    except Exception as e:
                        print(f"❌ Error copying WebP {filename}: {e}")
            
            print(f"✅ Copied {webp_count} WebP images")
    
    print("🎯 PROJECT-ONLY recovery finished!")
    print("🔍 Check your Django admin now - ALL project images should be visible!")
    
    # Show what we have now
    print("\n📊 Current projects folder contents:")
    if os.path.exists(projects_dir):
        project_files = len([f for f in os.listdir(projects_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Main Project Images: {project_files}")
    
    if os.path.exists(projects_albums_dir):
        project_album_files = len([f for f in os.listdir(projects_albums_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Project Album Images: {project_album_files}")
        print(f"   TOTAL Project Images: {project_files + project_album_files}")
    
    # Check database
    print("\n🗄️ Database check:")
    try:
        project_count = Project.objects.count()
        project_image_count = ProjectImage.objects.count()
        print(f"   Projects in DB: {project_count}")
        print(f"   Project Images in DB: {project_image_count}")
        
        if project_count > 0:
            print(f"   Expected: ~28-29 projects with ~223 images")
            print(f"   Recovery: {project_count} projects with {project_image_count} images")
    except Exception as e:
        print(f"   Database check error: {e}")

if __name__ == "__main__":
    try:
        recover_projects_only()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
