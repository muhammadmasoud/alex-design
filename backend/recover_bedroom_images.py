#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def recover_bedroom_images():
    print("🛏️ Recovering bedroom design images...")
    
    cache_dir = Path("media/cache")
    projects_dir = Path("media/projects")
    albums_dir = projects_dir / "albums"
    
    # Create directories if they don't exist
    projects_dir.mkdir(exist_ok=True)
    albums_dir.mkdir(exist_ok=True)
    
    # Find all bedroom-related images in cache
    bedroom_images = []
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if 'bedroom' in file.lower() or 'master-bedroom' in file.lower():
                bedroom_images.append(os.path.join(root, file))
    
    print(f"Found {len(bedroom_images)} bedroom images")
    
    # Copy them to projects/albums
    for image_path in bedroom_images:
        filename = os.path.basename(image_path)
        dest_path = albums_dir / filename
        
        try:
            shutil.copy2(image_path, dest_path)
            print(f"✅ Copied: {filename}")
        except Exception as e:
            print(f"❌ Error copying {filename}: {e}")
    
    print("🎯 Bedroom images recovery complete!")

if __name__ == "__main__":
    recover_bedroom_images()
