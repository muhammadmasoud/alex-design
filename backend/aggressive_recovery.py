#!/usr/bin/env python3
"""
Aggressive recovery - copy ALL cached images to projects directory
"""
import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def aggressive_recovery():
    print("🚨 AGGRESSIVE RECOVERY MODE - Copying ALL cached images...")
    
    media_root = Path('media')
    cache_dir = media_root / 'cache'
    
    if not cache_dir.exists():
        print("❌ Cache directory not found!")
        return
    
    # Create all necessary directories
    projects_dir = media_root / 'projects'
    projects_dir.mkdir(exist_ok=True)
    
    albums_dir = projects_dir / 'albums'
    albums_dir.mkdir(exist_ok=True)
    
    # Get ALL cached images
    all_cached = []
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                all_cached.append(os.path.join(root, file))
    
    print(f"📁 Found {len(all_cached)} total cached images")
    
    # Copy EVERYTHING to projects/albums
    copied_count = 0
    for cache_path in all_cached:
        try:
            filename = os.path.basename(cache_path)
            dest_path = albums_dir / filename
            
            # Always copy, overwrite if exists
            shutil.copy2(cache_path, dest_path)
            copied_count += 1
            
            if copied_count % 50 == 0:  # Progress indicator
                print(f"📊 Copied {copied_count} images...")
                
        except Exception as e:
            print(f"❌ Error copying {filename}: {e}")
    
    print(f"🎯 AGGRESSIVE RECOVERY COMPLETE! Copied {copied_count} images")
    print("🔍 Now run: python fix_database_image_paths.py")

if __name__ == "__main__":
    try:
        aggressive_recovery()
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
        import traceback
        traceback.print_exc()
