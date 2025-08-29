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
    
    # Strategy: Keep only the BEST optimized versions and remove everything else
    
    # 1. Remove projects folder (contains original uploads)
    if projects_dir.exists():
        print(f"\n🗑️  Removing projects folder (original uploads)...")
        try:
            import shutil
            shutil.rmtree(projects_dir)
            print(f"✅ Removed projects folder")
        except Exception as e:
            print(f"❌ Error removing projects folder: {e}")
    
    # 2. Remove services folder (contains original uploads)
    if services_dir.exists():
        print(f"\n🗑️  Removing services folder (original uploads)...")
        try:
            import shutil
            shutil.rmtree(services_dir)
            print(f"✅ Removed services folder")
        except Exception as e:
            print(f"❌ Error removing services folder: {e}")
    
    # 3. Clean up optimized folder - keep only the best versions
    if optimized_dir.exists():
        print(f"\n🔍 Cleaning optimized folder...")
        optimized_files = list(optimized_dir.rglob("*"))
        image_files = [f for f in optimized_files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
        
        # Group files by base name
        file_groups = {}
        for img_file in image_files:
            base_name = img_file.stem
            if '_' in base_name:
                # Remove quality/size suffixes to get base name
                parts = base_name.split('_')
                if len(parts) > 2:
                    base_name = '_'.join(parts[:-2])
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(img_file)
        
        # Keep only the best version of each image
        files_removed = 0
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # Sort by file size (larger = better quality)
                files.sort(key=lambda x: x.stat().st_size, reverse=True)
                
                # Keep the largest file (best quality) and remove the rest
                best_file = files[0]
                for file_to_remove in files[1:]:
                    try:
                        file_to_remove.unlink()
                        files_removed += 1
                        print(f"🗑️  Removed duplicate: {file_to_remove.name}")
                    except Exception as e:
                        print(f"❌ Error removing {file_to_remove}: {e}")
        
        print(f"✅ Removed {files_removed} duplicate optimized files")
    
    # 4. Clean up webp folder - keep only the best versions
    if webp_dir.exists():
        print(f"\n🔍 Cleaning webp folder...")
        webp_files = list(webp_dir.rglob("*"))
        image_files = [f for f in webp_files if f.is_file() and f.suffix.lower() in ['.webp']]
        
        # Group files by base name
        file_groups = {}
        for img_file in image_files:
            base_name = img_file.stem
            if '_' in base_name:
                # Remove quality/size suffixes to get base name
                parts = base_name.split('_')
                if len(parts) > 2:
                    base_name = '_'.join(parts[:-2])
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(img_file)
        
        # Keep only the best version of each image
        files_removed = 0
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # Sort by file size (larger = better quality)
                files.sort(key=lambda x: x.stat().st_size, reverse=True)
                
                # Keep the largest file (best quality) and remove the rest
                best_file = files[0]
                for file_to_remove in files[1:]:
                    try:
                        file_to_remove.unlink()
                        files_removed += 1
                        print(f"🗑️  Removed duplicate: {file_to_remove.name}")
                    except Exception as e:
                        print(f"❌ Error removing {file_to_remove}: {e}")
        
        print(f"✅ Removed {files_removed} duplicate webp files")
    
    # Final storage check
    print(f"\n📊 Final storage check:")
    total_size = sum(f.stat().st_size for f in media_dir.rglob('*') if f.is_file())
    print(f"Total media size: {total_size / (1024*1024):.1f} MB")
    
    print("\n🎯 Cleanup complete! You now have only the best optimized images.")

def verify_cleanup():
    """Verify the cleanup was successful"""
    print("\n🔍 Verifying cleanup...")
    
    media_dir = Path(settings.MEDIA_ROOT)
    
    # Check what's left
    directories = {
        'media': media_dir,
        'projects': media_dir / "projects",
        'services': media_dir / "services", 
        'optimized': media_dir / "optimized",
        'webp': media_dir / "webp"
    }
    
    for name, directory in directories.items():
        if directory.exists():
            files = list(directory.rglob("*"))
            image_files = [f for f in files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
            size = sum(f.stat().st_size for f in image_files) if image_files else 0
            print(f"📁 {name}: {len(image_files)} files, {size / (1024*1024):.1f} MB")
        else:
            print(f"📁 {name}: Does not exist")
    
    print("✅ Verification complete!")

if __name__ == "__main__":
    try:
        cleanup_duplicate_images()
        verify_cleanup()
        print("\n🎉 All done! Your images are now clean and optimized.")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
