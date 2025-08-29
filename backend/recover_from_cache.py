#!/usr/bin/env python3
"""
Recover images from cache directory and fix database paths
"""
import os
import sys
import django
import shutil
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectImage

def recover_from_cache():
    """Recover images from cache directory"""
    print("🚨 Starting cache recovery...")
    
    media_root = Path('media')
    cache_dir = media_root / 'cache'
    
    if not cache_dir.exists():
        print("❌ Cache directory not found!")
        return
    
    # Get all cached images
    cached_images = []
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                cached_images.append(os.path.join(root, file))
    
    print(f"�� Found {len(cached_images)} cached images")
    
    # Create projects directory structure
    projects_dir = media_root / 'projects'
    projects_dir.mkdir(exist_ok=True)
    
    albums_dir = projects_dir / 'albums'
    albums_dir.mkdir(exist_ok=True)
    
    # Copy images from cache to projects directory
    copied_count = 0
    for cache_path in cached_images:
        try:
            # Get filename from cache path
            filename = os.path.basename(cache_path)
            
            # Determine destination based on filename
            if 'album' in filename:
                dest_path = albums_dir / filename
            else:
                dest_path = projects_dir / filename
            
            # Copy the image (use highest quality version if multiple exist)
            if not dest_path.exists() or 'q95' in cache_path or '1920x1080' in cache_path:
                shutil.copy2(cache_path, dest_path)
                copied_count += 1
                print(f"✅ Copied: {filename}")
                
        except Exception as e:
            print(f"❌ Error copying {filename}: {e}")
    
    print(f"�� Recovery complete! Copied {copied_count} images")
    print("🔍 Now run: python fix_database_image_paths.py")

if __name__ == "__main__":
    try:
        recover_from_cache()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
