#!/usr/bin/env python3
"""
Test script to demonstrate automatic folder structure creation
Run this script to see how the new folder structure works
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectImage
from django.utils.text import slugify
from django.conf import settings


def test_folder_creation():
    """Test the automatic folder structure creation"""
    
    print("🧪 Testing Automatic Folder Structure Creation")
    print("=" * 50)
    
    # Test project title
    test_title = "Modern Architecture Project"
    slugified_title = slugify(test_title)
    
    print(f"Project Title: {test_title}")
    print(f"Slugified Title: {slugified_title}")
    print()
    
    # Expected folder paths
    expected_project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', slugified_title)
    expected_album_folder = os.path.join(expected_project_folder, 'album')
    
    print("Expected Folder Structure:")
    print(f"📁 {expected_project_folder}/")
    print(f"  📁 album/")
    print()
    
    # Check if folders exist
    print("Current Status:")
    if os.path.exists(expected_project_folder):
        print(f"✅ Project folder exists: {expected_project_folder}")
    else:
        print(f"❌ Project folder does not exist: {expected_project_folder}")
    
    if os.path.exists(expected_album_folder):
        print(f"✅ Album folder exists: {expected_album_folder}")
    else:
        print(f"❌ Album folder does not exist: {expected_album_folder}")
    
    print()
    
    # Show current projects directory structure
    projects_dir = os.path.join(settings.MEDIA_ROOT, 'projects')
    if os.path.exists(projects_dir):
        print("Current Projects Directory Structure:")
        print(f"📁 {projects_dir}/")
        
        try:
            for item in os.listdir(projects_dir):
                item_path = os.path.join(projects_dir, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                    # Show contents of project folder
                    try:
                        for subitem in os.listdir(item_path):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isdir(subitem_path):
                                print(f"    📁 {subitem}/")
                            else:
                                print(f"    📄 {subitem}")
                    except PermissionError:
                        print(f"    🔒 Permission denied accessing {item}")
                else:
                    print(f"  📄 {item}")
        except PermissionError:
            print("  🔒 Permission denied accessing projects directory")
    else:
        print(f"❌ Projects directory does not exist: {projects_dir}")
    
    print()
    print("📝 Note: Folders will be created automatically when you:")
    print("  1. Create a new project through Django admin")
    print("  2. Create a new project through the frontend dashboard")
    print("  3. Add album images to a project")
    print()
    print("🎯 The system will automatically:")
    print("  • Create: media/projects/{project_name}/")
    print("  • Create: media/projects/{project_name}/album/")
    print("  • Store main project image in: media/projects/{project_name}/")
    print("  • Store album images in: media/projects/{project_name}/album/")
    print("  • Generate thumbnails in: media/projects/{project_name}/thumbnails/")
    print("  • Clean up folders when projects are deleted")


if __name__ == "__main__":
    test_folder_creation()
