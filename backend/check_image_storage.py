#!/usr/bin/env python
"""
Check current image storage and identify duplicates
This script will show you what images you have and where they are
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def check_image_storage():
    """Check current image storage and identify duplicates"""
    print("🔍 Checking image storage...")
    
    media_dir = Path(settings.MEDIA_ROOT)
    
    # Check each directory
    directories = {
        'media': media_dir,
        'projects': media_dir / "projects",
        'services': media_dir / "services", 
        'optimized': media_dir / "optimized",
        'webp': media_dir / "webp"
    }
    
    total_files = 0
    total_size = 0
    
    for name, directory in directories.items():
        if directory.exists():
            files = list(directory.rglob("*"))
            image_files = [f for f in files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
            
            if image_files:
                size = sum(f.stat().st_size for f in image_files)
                print(f"\n📁 {name.upper()} Directory:")
                print(f"   Files: {len(image_files)}")
                print(f"   Size: {size / (1024*1024):.1f} MB")
                
                # Show file types
                extensions = {}
                for f in image_files:
                    ext = f.suffix.lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
                
                for ext, count in extensions.items():
                    print(f"   {ext}: {count} files")
                
                total_files += len(image_files)
                total_size += size
            else:
                print(f"\n📁 {name.upper()} Directory: No image files")
        else:
            print(f"\n📁 {name.upper()} Directory: Does not exist")
    
    print(f"\n📊 TOTAL SUMMARY:")
    print(f"   Total image files: {total_files}")
    print(f"   Total size: {total_size / (1024*1024):.1f} MB")
    
    # Check for potential duplicates
    print(f"\n🔍 DUPLICATE ANALYSIS:")
    
    # Get all image files
    all_images = []
    for directory in directories.values():
        if directory.exists():
            for file_path in directory.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    all_images.append(file_path)
    
    # Check for files with similar names (potential duplicates)
    base_names = {}
    for img_path in all_images:
        base_name = img_path.stem
        if '_' in base_name:
            # Remove quality/size suffixes
            parts = base_name.split('_')
            if len(parts) > 2:
                base_name = '_'.join(parts[:-2])
        
        if base_name not in base_names:
            base_names[base_name] = []
        base_names[base_name].append(img_path)
    
    duplicates = {name: paths for name, paths in base_names.items() if len(paths) > 1}
    
    if duplicates:
        print(f"   Found {len(duplicates)} potential duplicate groups:")
        for base_name, paths in list(duplicates.items())[:10]:  # Show first 10
            print(f"     {base_name}: {len(paths)} files")
            for path in paths:
                size = path.stat().st_size / (1024*1024)
                print(f"       - {path.name} ({size:.1f} MB)")
    else:
        print("   No obvious duplicates found")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if total_size > 1000:  # More than 1GB
        print("   - Consider running cleanup_duplicate_images.py to remove duplicates")
        print("   - You may have original uploads + optimized versions")
    else:
        print("   - Storage looks reasonable")
    
    print("   - Run cleanup_duplicate_images.py to clean up duplicates")

if __name__ == "__main__":
    try:
        check_image_storage()
    except Exception as e:
        print(f"❌ Error during check: {e}")
        import traceback
        traceback.print_exc()
