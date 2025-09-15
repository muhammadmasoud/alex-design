#!/usr/bin/env python
"""
Test script to verify project deletion functionality
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectCategory, ProjectImage
from django.utils.text import slugify
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def create_test_image():
    """Create a simple test image file"""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile("test_image.jpg", img_io.getvalue(), content_type="image/jpeg")

def test_project_deletion():
    """Test complete project deletion including files and folders"""
    print("🧪 Starting Project Deletion Test...")
    
    # Create a test category
    category, created = ProjectCategory.objects.get_or_create(
        name="Test Category",
        defaults={'description': 'Test category for deletion testing'}
    )
    
    # Create a test project
    test_image = create_test_image()
    project = Project.objects.create(
        title="Test Project for Deletion",
        description="This is a test project that will be deleted",
        project_date="2024-01-01",
        image=test_image
    )
    project.categories.add(category)
    
    print(f"✅ Created test project: {project.title} (ID: {project.id})")
    
    # Create some album images
    album_image1 = ProjectImage.objects.create(
        project=project,
        image=create_test_image(),
        title="Album Image 1"
    )
    
    album_image2 = ProjectImage.objects.create(
        project=project,
        image=create_test_image(),
        title="Album Image 2"
    )
    
    print(f"✅ Created {project.album_images.count()} album images")
    
    # Check if project folder exists
    project_folder_name = slugify(project.title)[:50]
    project_folder_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder_name)
    
    print(f"📁 Expected project folder: {project_folder_path}")
    print(f"📁 Folder exists: {os.path.exists(project_folder_path)}")
    
    if project.image:
        print(f"🖼️  Main image path: {project.image.path}")
        print(f"🖼️  Main image exists: {os.path.exists(project.image.path)}")
    
    # Get album image paths before deletion
    album_paths = []
    for album_img in project.album_images.all():
        if album_img.image:
            album_paths.append(album_img.image.path)
            print(f"🖼️  Album image: {album_img.image.path}")
    
    # Now delete the project
    print("\n🗑️  Deleting project...")
    project_id = project.id
    project_title = project.title
    
    try:
        project.delete()
        print(f"✅ Successfully deleted project: {project_title} (ID: {project_id})")
        
        # Verify project is gone from database
        try:
            Project.objects.get(id=project_id)
            print("❌ ERROR: Project still exists in database!")
        except Project.DoesNotExist:
            print("✅ Project correctly removed from database")
        
        # Check if project folder is gone
        print(f"\n📁 Checking if project folder was deleted...")
        print(f"📁 Folder exists after deletion: {os.path.exists(project_folder_path)}")
        
        # Check if main image file is gone
        if os.path.exists(project_folder_path):
            print(f"⚠️  Project folder still exists: {project_folder_path}")
            print(f"📂 Contents: {os.listdir(project_folder_path) if os.path.exists(project_folder_path) else 'N/A'}")
        else:
            print("✅ Project folder successfully deleted")
        
        # Check album images
        for path in album_paths:
            if os.path.exists(path):
                print(f"⚠️  Album image still exists: {path}")
            else:
                print(f"✅ Album image deleted: {os.path.basename(path)}")
        
        # Check if album images are gone from database
        remaining_album_images = ProjectImage.objects.filter(project_id=project_id).count()
        if remaining_album_images > 0:
            print(f"❌ ERROR: {remaining_album_images} album images still in database!")
        else:
            print("✅ All album images removed from database")
            
    except Exception as e:
        print(f"❌ ERROR during project deletion: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Cleanup test category
    try:
        category.delete()
        print("🧹 Cleaned up test category")
    except:
        pass
    
    print("\n🏁 Project deletion test completed!")

if __name__ == "__main__":
    test_project_deletion()
