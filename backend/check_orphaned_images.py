#!/usr/bin/env python
"""
DRY RUN script to check for orphaned image files without deleting anything.
Run this first to see what would be cleaned up.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service, ProjectImage, ServiceImage

def get_database_images():
    """Get all image paths that are referenced in the database"""
    db_images = set()
    
    # Project main images
    for project in Project.objects.filter(image__isnull=False):
        if project.image and project.image.name:
            db_images.add(project.image.name)
    
    # Service icons
    for service in Service.objects.filter(icon__isnull=False):
        if service.icon and service.icon.name:
            db_images.add(service.icon.name)
    
    # Project album images
    for project_image in ProjectImage.objects.all():
        if project_image.image and project_image.image.name:
            db_images.add(project_image.image.name)
    
    # Service album images
    for service_image in ServiceImage.objects.all():
        if service_image.image and service_image.image.name:
            db_images.add(service_image.image.name)
    
    return db_images

def get_file_system_images():
    """Get all image files that exist on disk"""
    fs_images = set()
    media_root = settings.MEDIA_ROOT
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.bmp', '.tiff'}
    
    for root, dirs, files in os.walk(media_root):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # Get relative path from media root
                rel_path = os.path.relpath(os.path.join(root, file), media_root)
                # Normalize path separators
                rel_path = rel_path.replace('\\', '/')
                fs_images.add(rel_path)
    
    return fs_images

def analyze_images():
    """Analyze images without deleting anything"""
    print("🔍 Analyzing image files (DRY RUN - no files will be deleted)...")
    print("=" * 70)
    
    # Get images from database and file system
    db_images = get_database_images()
    fs_images = get_file_system_images()
    
    print(f"📊 Database images: {len(db_images)}")
    print(f"💾 File system images: {len(fs_images)}")
    
    # Find orphaned files
    orphaned = fs_images - db_images
    
    if not orphaned:
        print("✅ No orphaned files found!")
        return
    
    print(f"🗑️  Orphaned files found: {len(orphaned)}")
    
    # Calculate potential space savings
    total_size = 0
    for orphan in orphaned:
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, orphan)
            if os.path.exists(full_path):
                total_size += os.path.getsize(full_path)
        except:
            pass
    
    print(f"💾 Potential space savings: {total_size / (1024*1024):.2f} MB")
    
    # Show examples by category
    print("\n📋 Examples of orphaned files by type:")
    
    # Group by file extension
    by_extension = {}
    for orphan in orphaned:
        ext = os.path.splitext(orphan)[1].lower()
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(orphan)
    
    for ext, files in sorted(by_extension.items()):
        print(f"\n   {ext.upper()} files ({len(files)}):")
        for i, file in enumerate(files[:5]):
            print(f"     {i+1}. {file}")
        if len(files) > 5:
            print(f"     ... and {len(files) - 5} more")
    
    # Show some specific examples
    print(f"\n📋 Sample of orphaned files:")
    for i, orphan in enumerate(list(orphaned)[:20]):
        print(f"   {i+1:2d}. {orphan}")
    
    if len(orphaned) > 20:
        print(f"   ... and {len(orphaned) - 20} more")
    
    print(f"\n⚠️  This is a DRY RUN - no files were deleted!")
    print(f"💡 To actually delete these files, run: python cleanup_orphaned_images.py")

if __name__ == "__main__":
    print("🔍 Image Analysis Script (DRY RUN)")
    print("=" * 50)
    
    try:
        analyze_images()
    except Exception as e:
        print(f"\n💥 Error occurred: {e}")
        import traceback
        traceback.print_exc()
