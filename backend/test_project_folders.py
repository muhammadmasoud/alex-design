#!/usr/bin/env python3
"""
Test script to verify the new project folder structure works correctly.
This script will:
1. Create a test project
2. Upload images to verify folder creation
3. Check that the folder structure is correct
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from portfolio.models import Project, ProjectImage, ProjectCategory
from portfolio.enhanced_image_optimizer import optimize_uploaded_image
import tempfile
from PIL import Image


def create_test_image(width=800, height=600, color=(255, 0, 0)):
    """Create a test image for testing"""
    img = Image.new('RGB', (width, height), color)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    temp_file.close()
    
    return temp_file.name


def test_project_folder_creation():
    """Test that project folders are created automatically"""
    print("Testing project folder creation...")
    
    # Create a test project
    project = Project.objects.create(
        title="Test Project for Folder Creation",
        description="This is a test project to verify folder creation",
        project_date="2024-01-01"
    )
    
    print(f"Created test project: {project.title} (ID: {project.pk})")
    
    # Check if folders were created
    project_folder = f"project_{project.pk}"
    project_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder)
    album_path = os.path.join(project_path, 'album')
    
    print(f"Expected project path: {project_path}")
    print(f"Expected album path: {album_path}")
    
    # Verify folders exist
    if os.path.exists(project_path):
        print(f"✓ Project folder created: {project_path}")
    else:
        print(f"✗ Project folder not created: {project_path}")
        return False
    
    if os.path.exists(album_path):
        print(f"✓ Album folder created: {album_path}")
    else:
        print(f"✗ Album folder not created: {album_path}")
        return False
    
    return True


def test_image_upload_to_project_folder():
    """Test that images are uploaded to the correct project folder"""
    print("\nTesting image upload to project folder...")
    
    # Get the test project
    project = Project.objects.filter(title="Test Project for Folder Creation").first()
    if not project:
        print("✗ Test project not found")
        return False
    
    # Create a test image
    test_image_path = create_test_image(800, 600, (0, 255, 0))
    
    try:
        # Upload the image to the project
        with open(test_image_path, 'rb') as img_file:
            # Create a ContentFile
            content = img_file.read()
            image_file = ContentFile(content, name='test_project_image.png')
            
            # Save the image to the project
            project.image.save('test_project_image.png', image_file, save=True)
            
            print(f"✓ Project image uploaded: {project.image.name}")
            
            # Check if the image is in the correct folder
            expected_path = f"projects/project_{project.pk}/test_project_image.png"
            if project.image.name == expected_path:
                print(f"✓ Image saved to correct path: {project.image.name}")
            else:
                print(f"✗ Image saved to wrong path. Expected: {expected_path}, Got: {project.image.name}")
                return False
            
            # Check if the file actually exists
            if default_storage.exists(project.image.name):
                print(f"✓ Image file exists in storage")
            else:
                print(f"✗ Image file not found in storage")
                return False
                
        return True
        
    finally:
        # Clean up test image file
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)


def test_album_image_upload():
    """Test that album images are uploaded to the correct album folder"""
    print("\nTesting album image upload...")
    
    # Get the test project
    project = Project.objects.filter(title="Test Project for Folder Creation").first()
    if not project:
        print("✗ Test project not found")
        return False
    
    # Create a test album image
    test_image_path = create_test_image(1200, 800, (0, 0, 255))
    
    try:
        # Upload the image to the project album
        with open(test_image_path, 'rb') as img_file:
            # Create a ContentFile
            content = img_file.read()
            image_file = ContentFile(content, name='test_album_image.png')
            
            # Create a project image
            project_image = ProjectImage.objects.create(
                project=project,
                title="Test Album Image",
                description="This is a test album image",
                order=1
            )
            
            # Save the image
            project_image.image.save('test_album_image.png', image_file, save=True)
            
            print(f"✓ Album image uploaded: {project_image.image.name}")
            
            # Check if the image is in the correct folder
            expected_path = f"projects/project_{project.pk}/album/test_album_image.png"
            if project_image.image.name == expected_path:
                print(f"✓ Album image saved to correct path: {project_image.image.name}")
            else:
                print(f"✗ Album image saved to wrong path. Expected: {expected_path}, Got: {project_image.image.name}")
                return False
            
            # Check if the file actually exists
            if default_storage.exists(project_image.image.name):
                print(f"✓ Album image file exists in storage")
            else:
                print(f"✗ Album image file not found in storage")
                return False
                
        return True
        
    finally:
        # Clean up test image file
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)


def test_folder_structure():
    """Test the complete folder structure"""
    print("\nTesting complete folder structure...")
    
    # Get the test project
    project = Project.objects.filter(title="Test Project for Folder Creation").first()
    if not project:
        print("✗ Test project not found")
        return False
    
    project_folder = f"project_{project.pk}"
    project_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder)
    album_path = os.path.join(project_path, 'album')
    
    print(f"Project folder: {project_path}")
    print(f"Album folder: {album_path}")
    
    # List contents
    if os.path.exists(project_path):
        print(f"\nProject folder contents:")
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                # List album contents
                if item == 'album':
                    for album_item in os.listdir(item_path):
                        album_item_path = os.path.join(item_path, album_item)
                        if os.path.isfile(album_item_path):
                            size = os.path.getsize(album_item_path)
                            print(f"    📄 {album_item} ({size} bytes)")
            elif os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  📄 {item} ({size} bytes)")
    
    return True


def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test project (this will also delete associated images)
    project = Project.objects.filter(title="Test Project for Folder Creation").first()
    if project:
        project.delete()
        print("✓ Test project deleted")
    
    # Check if folders were cleaned up
    project_folder = f"project_{project.pk if project else 'unknown'}"
    project_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder)
    
    if os.path.exists(project_path):
        print(f"⚠ Project folder still exists: {project_path}")
        print("   You may need to manually delete this folder")
    else:
        print("✓ Project folder cleaned up")


def main():
    """Main test function"""
    print("=" * 60)
    print("Testing Project Folder Structure")
    print("=" * 60)
    
    try:
        # Run tests
        if not test_project_folder_creation():
            print("✗ Project folder creation test failed")
            return
        
        if not test_image_upload_to_project_folder():
            print("✗ Project image upload test failed")
            return
        
        if not test_album_image_upload():
            print("✗ Album image upload test failed")
            return
        
        if not test_folder_structure():
            print("✗ Folder structure test failed")
            return
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! Project folder structure is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        cleanup_test_data()


if __name__ == "__main__":
    main()
