#!/usr/bin/env python
"""
Test script to verify project deletion functionality with optimized images
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectCategory, ProjectImage
from portfolio.image_optimizer import ImageOptimizer
from django.utils.text import slugify
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import time

def create_test_image(size=(500, 500)):
    """Create a simple test image file"""
    img = Image.new('RGB', size, color='blue')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile("test_image.jpg", img_io.getvalue(), content_type="image/jpeg")

def test_project_deletion_with_optimized_images():
    """Test complete project deletion including optimized images"""
    print("🧪 Starting Project Deletion Test with Optimized Images...")
    
    # Create a test category
    category, created = ProjectCategory.objects.get_or_create(
        name="Test Category Optimized",
        defaults={'description': 'Test category for optimized deletion testing'}
    )
    
    # Create a test project with a larger image (to trigger optimization)
    test_image = create_test_image(size=(800, 600))
    project = Project.objects.create(
        title="Test Project with Optimized Images",
        description="This project will have optimized images that need to be deleted",
        project_date="2024-01-01",
        image=test_image
    )
    project.categories.add(category)
    
    print(f"✅ Created test project: {project.title} (ID: {project.id})")
    
    # Create some album images
    album_image1 = ProjectImage.objects.create(
        project=project,
        image=create_test_image(size=(600, 400)),
        title="Large Album Image 1"
    )
    
    album_image2 = ProjectImage.objects.create(
        project=project,
        image=create_test_image(size=(700, 500)),
        title="Large Album Image 2"
    )
    
    print(f"✅ Created {project.album_images.count()} album images")
    
    # Wait for optimization to complete and then manually trigger it to ensure it's done
    print("⏳ Waiting for automatic optimization...")
    time.sleep(3)
    
    # Manually trigger optimization to ensure it's complete
    print("🔧 Manually triggering optimization to ensure completion...")
    try:
        success, message = project.optimize_images_manually()
        print(f"Optimization result: {success} - {message}")
    except Exception as e:
        print(f"Optimization error: {e}")
    
    # Check project folder and optimized files
    project_folder_name = slugify(project.title)[:50]
    project_folder_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder_name)
    webp_folder_path = os.path.join(project_folder_path, 'webp')
    
    print(f"\n📁 Project folder: {project_folder_path}")
    print(f"📁 Folder exists: {os.path.exists(project_folder_path)}")
    print(f"📁 WebP folder: {webp_folder_path}")
    print(f"📁 WebP folder exists: {os.path.exists(webp_folder_path)}")
    
    if os.path.exists(webp_folder_path):
        webp_files = []
        for root, dirs, files in os.walk(webp_folder_path):
            for file in files:
                if file.endswith('.webp'):
                    webp_files.append(os.path.join(root, file))
        
        print(f"🖼️  Found {len(webp_files)} optimized .webp files:")
        for webp_file in webp_files:
            print(f"    📄 {os.path.relpath(webp_file, project_folder_path)}")
    
    # Check optimized paths in database
    print(f"\n🗄️  Database optimized paths:")
    print(f"    Main optimized: {project.optimized_image}")
    print(f"    Main small: {project.optimized_image_small}")
    print(f"    Main medium: {project.optimized_image_medium}")
    print(f"    Main large: {project.optimized_image_large}")
    
    for i, album_img in enumerate(project.album_images.all(), 1):
        print(f"    Album {i} optimized: {album_img.optimized_image}")
    
    # Now delete the project
    print(f"\n🗑️  Deleting project with optimized images...")
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
        
        # Check if entire project folder is gone (including optimized images)
        print(f"\n📁 Checking if entire project folder was deleted...")
        print(f"📁 Project folder exists: {os.path.exists(project_folder_path)}")
        print(f"📁 WebP folder exists: {os.path.exists(webp_folder_path)}")
        
        if os.path.exists(project_folder_path):
            print(f"⚠️  Project folder still exists!")
            remaining_files = []
            for root, dirs, files in os.walk(project_folder_path):
                for file in files:
                    remaining_files.append(os.path.join(root, file))
            print(f"📂 Remaining files: {remaining_files}")
        else:
            print("✅ Complete project folder (including optimized images) successfully deleted")
        
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
    
    print("\n🏁 Project deletion test with optimized images completed!")

if __name__ == "__main__":
    test_project_deletion_with_optimized_images()
