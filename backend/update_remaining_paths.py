#!/usr/bin/env python3
"""
Update database paths for the remaining 3 projects
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

from portfolio.models import Project

def update_remaining_paths():
    print("�� Updating remaining project paths...")
    
    # Update the 3 projects with missing images
    updates = [
        ("Modern Hotel Facade Design & Execution Drawings", "projects/albums/modern-hotel-facade-design-execution-drawings_20250819_004628_5036dacd.jpg"),
        ("Office Building | nterior Design | Execution Drawing", "projects/albums/office-building-nterior-design-execution-drawing_20250821_011317_f83f8ebd.jpg"),
        ("Exhibition Pavilion", "projects/albums/exhibition-pavilion_20250821_083858_08555692.jpg")
    ]
    
    for project_title, new_path in updates:
        try:
            project = Project.objects.get(title__icontains=project_title.split('|')[0].strip())
            project.image.name = new_path
            project.save()
            print(f"✅ Updated: {project_title}")
        except Project.DoesNotExist:
            print(f"❌ Project not found: {project_title}")
        except Exception as e:
            print(f"❌ Error updating {project_title}: {e}")
    
    print("🎯 Path updates complete!")

if __name__ == "__main__":
    try:
        update_remaining_paths()
    except Exception as e:
        print(f"❌ Error during path updates: {e}")
        import traceback
        traceback.print_exc()
