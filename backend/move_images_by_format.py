#!/usr/bin/env python
"""
Move images by format - WebP vs others (saves disk space)
This script will organize your images into separate directories by format
"""
import os
import sys
import shutil
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def move_images_by_format():
    """Move WebP images to separate directory from other formats"""
    print("🔄 Starting image format separation (moving files)...")
    
    media_root = Path(settings.MEDIA_ROOT)
    projects_dir = Path(settings.MEDIA_ROOT).parent / "projects"
    
    # Create organized directories
    webp_dir = media_root / "webp_only"
    other_formats_dir = media_root / "other_formats"
    
    # Ensure directories exist
    webp_dir.mkdir(exist_ok=True)
    other_formats_dir.mkdir(exist_ok=True)
    
    print(f"📁 WebP directory: {webp_dir}")
    print(f"📁 Other formats directory: {other_formats_dir}")
    
    # Track counts and sizes
    webp_count = 0
    webp_size = 0
    other_count = 0
    other_size = 0
    
    # Process both media and projects directories
    source_dirs = [media_root, projects_dir]
    
    for source_dir in source_dirs:
        if not source_dir.exists():
            print(f"⚠️  Directory {source_dir} does not exist, skipping...")
            continue
            
        print(f"\n🔍 Processing {source_dir}...")
        
        # Find all image files
        for file_path in source_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.bmp', '.tif', '.tiff']:
                
                # Skip if file is already in our organized directories
                if 'webp_only' in str(file_path) or 'other_formats' in str(file_path):
                    continue
                
                # Get relative path for organizing
                rel_path = file_path.relative_to(source_dir)
                
                # Determine destination based on format
                if file_path.suffix.lower() == '.webp':
                    dest_dir = webp_dir
                    dest_path = dest_dir / rel_path
                    webp_count += 1
                    webp_size += file_path.stat().st_size
                else:
                    dest_dir = other_formats_dir
                    dest_path = dest_dir / rel_path
                    other_count += 1
                    other_size += file_path.stat().st_size
                
                # Create destination directory structure
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file (saves disk space)
                try:
                    shutil.move(str(file_path), str(dest_path))
                    if webp_count % 100 == 0 or other_count % 100 == 0:
                        print(f"   Moved: {webp_count} WebP, {other_count} others...")
                except Exception as e:
                    print(f"❌ Error moving {file_path}: {e}")
    
    # Summary
    print(f"\n📊 SEPARATION COMPLETE!")
    print(f"   WebP images: {webp_count} files, {webp_size / (1024*1024):.1f} MB")
    print(f"   Other formats: {other_count} files, {other_size / (1024*1024):.1f} MB")
    print(f"   Total: {webp_count + other_count} files, {(webp_size + other_size) / (1024*1024):.1f} MB")
    
    # Show directory structure
    print(f"\n📁 Directory structure:")
    print(f"   {webp_dir}")
    print(f"   {other_formats_dir}")
    
    return {
        'webp_count': webp_count,
        'webp_size': webp_size,
        'other_count': other_count,
        'other_size': other_size
    }

def verify_separation():
    """Verify the separation was successful"""
    print("\n🔍 Verifying separation...")
    
    webp_dir = Path(settings.MEDIA_ROOT) / "webp_only"
    other_formats_dir = Path(settings.MEDIA_ROOT) / "other_formats"
    
    if webp_dir.exists():
        webp_files = list(webp_dir.rglob("*.webp"))
        print(f"📁 WebP directory: {len(webp_files)} .webp files")
        
        # Check for non-WebP files in WebP directory
        non_webp_in_webp = [f for f in webp_dir.rglob("*") if f.is_file() and f.suffix.lower() != '.webp']
        if non_webp_in_webp:
            print(f"⚠️  Found {len(non_webp_in_webp)} non-WebP files in WebP directory")
        else:
            print("✅ WebP directory contains only WebP files")
    
    if other_formats_dir.exists():
        other_files = [f for f in other_formats_dir.rglob("*") if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.tif', '.tiff']]
        print(f"📁 Other formats directory: {len(other_files)} non-WebP files")
        
        # Check for WebP files in other formats directory
        webp_in_other = list(other_formats_dir.rglob("*.webp"))
        if webp_in_other:
            print(f"⚠️  Found {len(webp_in_other)} WebP files in other formats directory")
        else:
            print("✅ Other formats directory contains no WebP files")

if __name__ == "__main__":
    try:
        print("🔄 IMAGE FORMAT SEPARATION SCRIPT (MOVE MODE)")
        print("=" * 50)
        print("⚠️  This script will MOVE files (not copy) to save disk space")
        print("💡 Original files will be reorganized into new directories")
        
        # Run separation
        stats = move_images_by_format()
        
        # Verify results
        verify_separation()
        
        print("\n🎉 Image separation completed successfully!")
        print(f"💡 You can now find:")
        print(f"   - WebP images in: backend/media/webp_only/")
        print(f"   - Other formats in: backend/media/other_formats/")
        
    except Exception as e:
        print(f"❌ Error during separation: {e}")
        import traceback
        traceback.print_exc()
