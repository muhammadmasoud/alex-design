#!/usr/bin/env python
"""
Clean up duplicate images and keep only optimized versions
This script will remove original uploads and keep only the optimized versions
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

from portfolio.models import Project, Service, ProjectImage, ServiceImage
from portfolio.image_optimizer import ImageOptimizer

def cleanup_duplicate_images():
    """Remove duplicate images and keep only optimized versions"""
    print("🧹 Starting duplicate image cleanup...")
    
    # Check what exists in media folders
    media_dir = Path(settings.MEDIA_ROOT)
    projects_dir = media_dir / "projects"
    services_dir = media_dir / "services"
    optimized_dir = media_dir / "optimized"
    webp_dir = media_dir / "webp"
    
    print(f"📁 Media directory: {media_dir}")
    print(f"📁 Projects directory: {projects_dir}")
    print(f"📁 Services directory: {services_dir}")
    print(f"📁 Optimized directory: {optimized_dir}")
    print(f"📁 WebP directory: {webp_dir}")
    
    # Check if optimized versions exist
    if not optimized_dir.exists():
        print("❌ Optimized directory doesn't exist. Run reoptimize_images_hq.py first!")
        return
    
    # Get all optimized image files
    optimized_files = set()
    if optimized_dir.exists():
        for file_path in optimized_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                # Get the base name without optimization suffixes
                base_name = file_path.stem
                if '_' in base_name:
                    # Remove quality/size suffixes
                    parts = base_name.split('_')
                    if len(parts) > 2:
                        # Keep only the original filename part
                        base_name = '_'.join(parts[:-2])
                optimized_files.add(base_name)
    
    print(f"✅ Found {len(optimized_files)} optimized image versions")
    
    # Check for duplicates in projects folder
    if projects_dir.exists():
        print(f"\n🔍 Checking projects folder for duplicates...")
        project_files = list(projects_dir.rglob("*"))
        project_images = [f for f in project_files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
        duplicates_found = 0
        for img_file in project_images:
            base_name = img_file.stem
            if base_name in optimized_files:
                print(f"🗑️  Removing duplicate: {img_file}")
                try:
                    img_file.unlink()
                    duplicates_found += 1
                except Exception as e:
                    print(f"❌ Error removing {img_file}: {e}")
        
        print(f"✅ Removed {duplicates_found} duplicate project images")
    
    # Check for duplicates in services folder
    if services_dir.exists():
        print(f"\n🔍 Checking services folder for duplicates...")
        service_files = list(services_dir.rglob("*"))
        service_images = [f for f in service_files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
        duplicates_found = 0
        for img_file in service_images:
            base_name = img_file.stem
            if base_name in optimized_files:
                print(f"🗑️  Removing duplicate: {img_file}")
                try:
                    img_file.unlink()
                    duplicates_found += 1
                except Exception as e:
                    print(f"❌ Error removing {img_file}: {e}")
        
        print(f"✅ Removed {duplicates_found} duplicate service images")
    
    # Check for old low-quality optimized versions
    print(f"\n🔍 Checking for old low-quality optimized versions...")
    old_versions_removed = 0
    
    if optimized_dir.exists():
        for file_path in optimized_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                filename = file_path.name
                # Look for old quality indicators (85, 80, etc.)
                if any(quality in filename for quality in ['_85_', '_80_', '_70_', '_60_']):
                    print(f"🗑️  Removing old low-quality version: {file_path}")
                    try:
                        file_path.unlink()
                        old_versions_removed += 1
                    except Exception as e:
                        print(f"❌ Error removing {file_path}: {e}")
    
    print(f"✅ Removed {old_versions_removed} old low-quality versions")
    
    # Final storage check
    print(f"\n📊 Final storage check:")
    total_size = sum(f.stat().st_size for f in media_dir.rglob('*') if f.is_file())
    print(f"Total media size: {total_size / (1024*1024):.1f} MB")
    
    print("\n🎯 Cleanup complete! You now have only optimized images.")

def verify_optimized_images():
    """Verify that all images have optimized versions"""
    print("\n🔍 Verifying optimized images...")
    
    # Check projects
    projects = Project.objects.all()
    for project in projects:
        if project.image:
            optimized_path = ImageOptimizer.get_optimized_path(project.image.name, 'md', 'webp', 'high')
            if not os.path.exists(optimized_path):
                print(f"⚠️  Project {project.title} missing optimized image: {optimized_path}")
    
    # Check services
    services = Service.objects.all()
    for service in services:
        if service.icon:
            optimized_path = ImageOptimizer.get_optimized_path(service.icon.name, 'md', 'webp', 'high')
            if not os.path.exists(optimized_path):
                print(f"⚠️  Service {service.name} missing optimized image: {optimized_path}")
    
    print("✅ Verification complete!")

if __name__ == "__main__":
    try:
        cleanup_duplicate_images()
        verify_optimized_images()
        print("\n🎉 All done! Your images are now clean and optimized.")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
