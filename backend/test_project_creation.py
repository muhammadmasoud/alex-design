#!/usr/bin/env python3
"""
Simple test script to verify project creation works
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectCategory
from django.utils import timezone
from django.core.exceptions import ValidationError


def test_project_creation():
    """Test creating a simple project"""
    
    print("🧪 Testing Project Creation")
    print("=" * 40)
    
    try:
        # Create a test project with all required fields
        project_data = {
            'title': 'Test Project',
            'description': 'This is a test project to verify creation works',
            'project_date': timezone.now().date(),
            'order': 1
        }
        
        print("📝 Project data:")
        for key, value in project_data.items():
            print(f"   {key}: {value}")
        
        print(f"\n🔄 Creating project...")
        
        # Create the project
        project = Project.objects.create(**project_data)
        
        print(f"✅ Project created successfully!")
        print(f"   ID: {project.pk}")
        print(f"   Title: {project.title}")
        print(f"   Description: {project.description}")
        print(f"   Project Date: {project.project_date}")
        print(f"   Order: {project.order}")
        
        # Check if folders were created
        import os
        from django.conf import settings
        from django.utils.text import slugify
        
        project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', slugify(project.title))
        album_folder = os.path.join(project_folder, 'album')
        
        print(f"\n📁 Checking folder creation:")
        print(f"   Project folder: {project_folder}")
        print(f"   Album folder: {album_folder}")
        
        if os.path.exists(project_folder):
            print(f"   ✅ Project folder exists")
        else:
            print(f"   ❌ Project folder does not exist")
        
        if os.path.exists(album_folder):
            print(f"   ✅ Album folder exists")
        else:
            print(f"   ❌ Album folder does not exist")
        
        # Test validation
        print(f"\n🔍 Testing validation...")
        try:
            project.full_clean()
            print(f"   ✅ Validation passed")
        except ValidationError as e:
            print(f"   ❌ Validation failed: {e}")
        
        # Clean up - delete the test project
        print(f"\n🧹 Cleaning up...")
        project.delete()
        print(f"   ✅ Test project deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_project_validation():
    """Test project validation"""
    
    print(f"\n🔍 Testing Project Validation")
    print("=" * 40)
    
    try:
        # Test missing required fields
        print("Testing missing title...")
        project = Project()
        project.description = "Test description"
        project.project_date = timezone.now().date()
        
        try:
            project.full_clean()
            print("   ❌ Should have failed validation for missing title")
        except ValidationError as e:
            print(f"   ✅ Correctly failed validation: {e}")
        
        # Test missing description
        print("Testing missing description...")
        project = Project()
        project.title = "Test Title"
        project.project_date = timezone.now().date()
        
        try:
            project.full_clean()
            print("   ✅ Validation passed for missing description (it's optional)")
        except ValidationError as e:
            print(f"   ❌ Unexpected validation failure: {e}")
        
        # Test missing project_date
        print("Testing missing project_date...")
        project = Project()
        project.title = "Test Title"
        project.description = "Test description"
        
        try:
            project.full_clean()
            print("   ❌ Should have failed validation for missing project_date")
        except ValidationError as e:
            print(f"   ✅ Correctly failed validation: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in validation test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Project Creation Tests\n")
    
    success1 = test_project_creation()
    success2 = test_project_validation()
    
    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
