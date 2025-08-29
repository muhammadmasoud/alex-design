#!/usr/bin/env python3
"""
Enhanced database fix - more aggressive path fixing
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectImage

def enhanced_fix():
    print("🔧 Enhanced database fix...")
    
    # Get all projects
    projects = Project.objects.all()
    print(f"📊 Found {projects.count()} projects")
    
    # Fix each project
    fixed_count = 0
    for project in projects:
        try:
            if project.image:
                # Check if image exists
                image_path = f"media/{project.image.name}"
                if not os.path.exists(image_path):
                    print(f"❌ Missing image for {project.title}: {project.image.name}")
                    
                    # Try to find it in albums directory
                    filename = os.path.basename(project.image.name)
                    albums_path = f"media/projects/albums/{filename}"
                    
                    if os.path.exists(albums_path):
                        print(f"✅ Found in albums: {filename}")
                        # Update the database path
                        project.image.name = f"projects/albums/{filename}"
                        project.save()
                        fixed_count += 1
                    else:
                        print(f"❌ Not found in albums either: {filename}")
            
            # Fix album images
            album_images = ProjectImage.objects.filter(project=project)
            for album_img in album_images:
                if album_img.image:
                    img_path = f"media/{album_img.image.name}"
                    if not os.path.exists(img_path):
                        filename = os.path.basename(album_img.image.name)
                        albums_path = f"media/projects/albums/{filename}"
                        
                        if os.path.exists(albums_path):
                            album_img.image.name = f"projects/albums/{filename}"
                            album_img.save()
                            fixed_count += 1
                            
        except Exception as e:
            print(f"❌ Error fixing {project.title}: {e}")
    
    print(f"🎯 Enhanced fix complete! Fixed {fixed_count} image paths")

if __name__ == "__main__":
    try:
        enhanced_fix()
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
