#!/usr/bin/env python3
"""
Final fix for the remaining 3 broken images
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

from portfolio.models import Project

def final_fix():
    print("🔧 Final fix for remaining broken images...")
    
    # These are the 3 missing images that are in services folder
    missing_images = [
        "modern-hotel-facade-design-execution-drawings_20250819_004628_5036dacd.jpg",
        "office-building-nterior-design-execution-drawing_20250821_011317_f83f8ebd.jpg", 
        "exhibition-pavilion_20250821_083858_08555692.jpg"
    ]
    
    services_dir = Path("media/services")
    projects_dir = Path("media/projects")
    albums_dir = projects_dir / "albums"
    
    # Copy the missing images from services to projects/albums
    for filename in missing_images:
        source_path = services_dir / filename
        dest_path = albums_dir / filename
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                print(f"✅ Copied: {filename}")
            except Exception as e:
                print(f"❌ Error copying {filename}: {e}")
        else:
            print(f"❌ Source not found: {filename}")
    
    print("�� Final fix complete!")

if __name__ == "__main__":
    try:
        final_fix()
    except Exception as e:
        print(f"❌ Error during final fix: {e}")
        import traceback
        traceback.print_exc()
