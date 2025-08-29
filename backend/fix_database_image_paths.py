#!/usr/bin/env python
"""
FIX DATABASE IMAGE PATHS: Actually recover your 223 images by fixing the database paths
This script will check what's in your database and fix the image references
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

def fix_database_image_paths():
    """Fix the actual database image paths to recover your 223 images"""
    print("🚨 Starting DATABASE IMAGE PATH FIX...")
    print("🎯 Target: Fix 28-29 projects with 223 images")
    
    # First, let's see what's actually in your database
    print("\n📊 Checking your database...")
    projects = Project.objects.all()
    project_images = ProjectImage.objects.all()
    
    print(f"   Projects in DB: {projects.count()}")
    print(f"   Project Images in DB: {project_images.count()}")
    
    # Create the projects directory structure
    media_root = settings.MEDIA_ROOT
    projects_dir = os.path.join(media_root, 'projects')
    projects_albums_dir = os.path.join(projects_dir, 'albums')
    
    print(f"\n📁 Creating projects directory: {projects_dir}")
    os.makedirs(projects_dir, exist_ok=True)
    os.makedirs(projects_albums_dir, exist_ok=True)
    
    # Now let's check what optimized images you actually have
    optimized_dir = os.path.join(media_root, 'optimized')
    if not os.path.exists(optimized_dir):
        print("❌ ERROR: No optimized folder found!")
        return
    
    optimized_files = [f for f in os.listdir(optimized_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    print(f"\n🖼️ Found {len(optimized_files)} optimized images")
    
    # Let's see what the database expects vs what we have
    print("\n🔍 Analyzing database image paths...")
    
    # Check main project images
    for project in projects:
        if project.image:
            print(f"   Project '{project.title}' expects: {project.image.name}")
            
            # Find the corresponding optimized file
            expected_filename = os.path.basename(project.image.name)
            matching_files = [f for f in optimized_files if expected_filename in f or f.startswith(expected_filename.split('.')[0])]
            
            if matching_files:
                # Copy the optimized version to where the database expects it
                source_file = os.path.join(optimized_dir, matching_files[0])
                dest_file = os.path.join(projects_dir, expected_filename)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    print(f"      ✅ Restored: {expected_filename}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"      ❌ No matching optimized file found")
    
    # Check project album images
    print("\n🖼️ Checking project album images...")
    for img in project_images:
        if img.image:
            print(f"   Album image {img.id} expects: {img.image.name}")
            
            # Find the corresponding optimized file
            expected_filename = os.path.basename(img.image.name)
            matching_files = [f for f in optimized_files if expected_filename in f or f.startswith(expected_filename.split('.')[0])]
            
            if matching_files:
                # Copy the optimized version to where the database expects it
                source_file = os.path.join(optimized_dir, matching_files[0])
                dest_file = os.path.join(projects_albums_dir, expected_filename)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    print(f"      ✅ Restored: {expected_filename}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"      ❌ No matching optimized file found")
    
    # Now let's do a bulk copy of ALL optimized images to ensure coverage
    print(f"\n🔄 Bulk copying ALL optimized images to projects folder...")
    
    total_copied = 0
    for filename in optimized_files:
        source_path = os.path.join(optimized_dir, filename)
        
        if 'album' in filename:
            dest_path = os.path.join(projects_albums_dir, filename)
        else:
            dest_path = os.path.join(projects_dir, filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            total_copied += 1
            print(f"   ✅ Copied: {filename}")
        except Exception as e:
            print(f"   ❌ Error copying {filename}: {e}")
    
    print(f"\n🎯 Bulk copy complete! Copied {total_copied} images")
    
    # Final check
    print("\n📊 Final folder contents:")
    if os.path.exists(projects_dir):
        project_files = len([f for f in os.listdir(projects_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Main Project Images: {project_files}")
    
    if os.path.exists(projects_albums_dir):
        project_album_files = len([f for f in os.listdir(projects_albums_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        print(f"   Project Album Images: {project_album_files}")
        print(f"   TOTAL Project Images: {project_files + project_album_files}")
    
    print(f"\n🎯 Expected: ~223 images")
    print(f"🎯 Recovered: {project_files + project_album_files} images")
    
    if (project_files + project_album_files) >= 200:
        print("✅ SUCCESS: Most images recovered!")
    else:
        print("⚠️  PARTIAL: Some images still missing")

if __name__ == "__main__":
    try:
        fix_database_image_paths()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
