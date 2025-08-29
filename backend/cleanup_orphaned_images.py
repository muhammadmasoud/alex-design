#!/usr/bin/env python
"""
Cleanup script to remove orphaned image files that exist on disk
but are not referenced in the database.
"""

import os
import django
from django.conf import settings
from django.core.files.storage import default_storage

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

def cleanup_orphaned_images():
    """Remove orphaned image files"""
    print("🔍 Analyzing image files...")
    
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
    
    # Show some examples
    print("\n📋 Examples of orphaned files:")
    for i, orphan in enumerate(list(orphaned)[:10]):
        print(f"   {i+1}. {orphan}")
    
    if len(orphaned) > 10:
        print(f"   ... and {len(orphaned) - 10} more")
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will delete {len(orphaned)} files!")
    response = input("Are you sure you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Delete orphaned files
    deleted_count = 0
    failed_count = 0
    
    print("\n🗑️  Deleting orphaned files...")
    
    for orphan in orphaned:
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, orphan)
            if os.path.exists(full_path):
                os.remove(full_path)
                deleted_count += 1
                if deleted_count % 100 == 0:
                    print(f"   Deleted {deleted_count} files...")
        except Exception as e:
            print(f"   ❌ Failed to delete {orphan}: {e}")
            failed_count += 1
    
    print(f"\n✅ Cleanup completed!")
    print(f"   Deleted: {deleted_count} files")
    print(f"   Failed: {failed_count} files")
    
    # Verify cleanup
    remaining_fs_images = get_file_system_images()
    print(f"\n📊 Final count:")
    print(f"   Database images: {len(db_images)}")
    print(f"   File system images: {len(remaining_fs_images)}")
    print(f"   Remaining orphaned: {len(remaining_fs_images - db_images)}")

if __name__ == "__main__":
    print("🧹 Image Cleanup Script")
    print("=" * 50)
    
    try:
        cleanup_orphaned_images()
    except KeyboardInterrupt:
        print("\n❌ Operation interrupted by user.")
    except Exception as e:
        print(f"\n💥 Error occurred: {e}")
        import traceback
        traceback.print_exc()
