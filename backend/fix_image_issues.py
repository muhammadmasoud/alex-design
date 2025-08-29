#!/usr/bin/env python3
"""
Fix any image issues caused by optimization
"""
import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service, ProjectImage, ServiceImage

def fix_image_issues():
    print("=== FIXING IMAGE ISSUES ===")
    
    # Check if there are any WebP files that replaced PNGs in the database
    issues_fixed = 0
    
    print("\n=== CHECKING PROJECT MAIN IMAGES ===")
    for p in Project.objects.all():
        if p.image and p.image.name.endswith('.webp'):
            # Check if original PNG exists
            png_name = p.image.name.replace('.webp', '.png')
            png_path = f"media/{png_name}"
            webp_path = f"media/{p.image.name}"
            
            if os.path.exists(png_path) and not os.path.exists(webp_path):
                # WebP file is missing but PNG exists, revert to PNG
                print(f"  Fixing {p.title}: {p.image.name} -> {png_name}")
                p.image.name = png_name
                p.save()
                issues_fixed += 1
    
    print("\n=== CHECKING SERVICE ICONS ===")
    for s in Service.objects.all():
        if s.icon and s.icon.name.endswith('.webp'):
            # Check if original PNG exists
            png_name = s.icon.name.replace('.webp', '.png')
            png_path = f"media/{png_name}"
            webp_path = f"media/{s.icon.name}"
            
            if os.path.exists(png_path) and not os.path.exists(webp_path):
                # WebP file is missing but PNG exists, revert to PNG
                print(f"  Fixing {s.name}: {s.icon.name} -> {png_name}")
                s.icon.name = png_name
                s.save()
                issues_fixed += 1
    
    print("\n=== CHECKING PROJECT ALBUM IMAGES ===")
    for img in ProjectImage.objects.all():
        if img.image and img.image.name.endswith('.webp'):
            # Check if original PNG exists
            png_name = img.image.name.replace('.webp', '.png')
            png_path = f"media/{png_name}"
            webp_path = f"media/{img.image.name}"
            
            if os.path.exists(png_path) and not os.path.exists(webp_path):
                # WebP file is missing but PNG exists, revert to PNG
                print(f"  Fixing album image: {img.image.name} -> {png_name}")
                img.image.name = png_name
                img.save()
                issues_fixed += 1
    
    print("\n=== CHECKING SERVICE ALBUM IMAGES ===")
    for img in ServiceImage.objects.all():
        if img.image and img.image.name.endswith('.webp'):
            # Check if original PNG exists
            png_name = img.image.name.replace('.webp', '.png')
            png_path = f"media/{png_name}"
            webp_path = f"media/{img.image.name}"
            
            if os.path.exists(png_path) and not os.path.exists(webp_path):
                # WebP file is missing but PNG exists, revert to PNG
                print(f"  Fixing service album image: {img.image.name} -> {png_name}")
                img.image.name = png_name
                img.save()
                issues_fixed += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Issues fixed: {issues_fixed}")
    
    if issues_fixed == 0:
        print("✅ No database issues found!")
        print("\nIf you're still seeing broken images, the issue might be:")
        print("1. Browser cache - try Ctrl+F5 to refresh")
        print("2. Django development server cache - restart the server")
        print("3. Frontend build cache - rebuild the frontend")
    else:
        print("✅ Database issues have been fixed!")

def revert_optimization():
    print("\n=== REVERTING OPTIMIZATION (if needed) ===")
    
    # Remove WebP files and keep only originals
    removed_files = []
    
    for root, dirs, files in os.walk("media"):
        for file in files:
            if file.endswith('.webp'):
                webp_path = os.path.join(root, file)
                # Check if corresponding PNG exists
                png_file = file.replace('.webp', '.png')
                png_path = os.path.join(root, png_file)
                
                if os.path.exists(png_path):
                    # Remove WebP since PNG exists
                    os.remove(webp_path)
                    removed_files.append(webp_path)
                    print(f"  Removed: {webp_path}")
    
    print(f"\nRemoved {len(removed_files)} WebP files to prevent conflicts")

if __name__ == '__main__':
    fix_image_issues()
    
    response = input("\nDo you want to completely revert the optimization (remove all WebP files)? (y/N): ")
    if response.lower() == 'y':
        revert_optimization()
        print("\n✅ Optimization completely reverted!")
