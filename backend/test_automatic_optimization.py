#!/usr/bin/env python
"""
Test Automatic Image Optimization and Display
This script tests that optimized images are automatically used everywhere
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service
from portfolio.image_optimizer import ImageOptimizer

def test_automatic_display_methods():
    """Test that the new display methods automatically return optimized images"""
    print("🧪 Testing Automatic Image Display Methods")
    print("=" * 50)
    
    # Test Projects
    print("\n📁 Testing Projects:")
    projects = Project.objects.all()[:3]  # Test first 3 projects
    
    for project in projects:
        print(f"\n  Project: {project.title}")
        
        if project.image:
            # Test main image display
            original_url = project.image.url
            display_url = project.get_display_image_url('medium', 'webp')
            
            print(f"    Main Image:")
            print(f"      Original: {original_url}")
            print(f"      Display:  {display_url}")
            print(f"      Using Optimized: {'✅' if display_url != original_url else '❌'}")
            
            # Test album images display
            if project.album_images.exists():
                print(f"    Album Images:")
                original_album = [img.image.url for img in project.album_images.all()[:2]]
                display_album = project.get_display_album_urls('small', 'webp')[:2]
                
                for i, (orig, disp) in enumerate(zip(original_album, display_album)):
                    print(f"      Image {i+1}:")
                    print(f"        Original: {orig}")
                    print(f"        Display:  {disp}")
                    print(f"        Using Optimized: {'✅' if disp != orig else '❌'}")
        else:
            print(f"    No main image")
    
    # Test Services
    print("\n🔧 Testing Services:")
    services = Service.objects.all()[:3]  # Test first 3 services
    
    for service in services:
        print(f"\n  Service: {service.name}")
        
        if service.icon:
            # Test icon display
            original_url = service.icon.url
            display_url = service.get_display_icon_url('medium', 'webp')
            
            print(f"    Icon:")
            print(f"      Original: {original_url}")
            print(f"      Display:  {display_url}")
            print(f"      Using Optimized: {'✅' if display_url != original_url else '❌'}")
            
            # Test album images display
            if service.album_images.exists():
                print(f"    Album Images:")
                original_album = [img.image.url for img in service.album_images.all()[:2]]
                display_album = service.get_display_album_urls('small', 'webp')[:2]
                
                for i, (orig, disp) in enumerate(zip(original_album, display_album)):
                    print(f"      Image {i+1}:")
                    print(f"        Original: {orig}")
                    print(f"        Display:  {disp}")
                    print(f"        Using Optimized: {'✅' if disp != orig else '❌'}")
        else:
            print(f"    No icon")

def test_optimization_status():
    """Check if images are actually optimized"""
    print("\n🔍 Checking Optimization Status")
    print("=" * 50)
    
    # Check if webp folders exist
    from django.conf import settings
    media_root = settings.MEDIA_ROOT
    
    print(f"\n📁 Media Root: {media_root}")
    
    # Check projects
    projects_dir = os.path.join(media_root, 'projects')
    if os.path.exists(projects_dir):
        print("\n  Projects:")
        for project_folder in os.listdir(projects_dir)[:3]:
            project_path = os.path.join(projects_dir, project_folder)
            webp_path = os.path.join(project_path, 'webp')
            
            if os.path.exists(webp_path):
                webp_files = [f for f in os.listdir(webp_path) if f.endswith('.webp')]
                print(f"    {project_folder}: {len(webp_files)} optimized images ✅")
            else:
                print(f"    {project_folder}: No optimization folder ❌")
    
    # Check services
    services_dir = os.path.join(media_root, 'services')
    if os.path.exists(services_dir):
        print("\n  Services:")
        for service_folder in os.listdir(services_dir)[:3]:
            service_path = os.path.join(services_dir, service_folder)
            webp_path = os.path.join(service_path, 'webp')
            
            if os.path.exists(webp_path):
                webp_files = [f for f in os.listdir(webp_path) if f.endswith('.webp')]
                print(f"    {service_folder}: {len(webp_files)} optimized images ✅")
            else:
                print(f"    {service_folder}: No optimization folder ❌")

def main():
    """Main test function"""
    print("🚀 Testing Automatic Image Optimization System")
    print("=" * 60)
    
    try:
        # Test display methods
        test_automatic_display_methods()
        
        # Test optimization status
        test_optimization_status()
        
        print("\n✅ Testing completed successfully!")
        print("\n💡 What this means:")
        print("   - If you see 'Using Optimized: ✅', the system is working!")
        print("   - If you see 'Using Optimized: ❌', images need optimization")
        print("   - Run 'python manage.py optimize_images' to optimize existing images")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
