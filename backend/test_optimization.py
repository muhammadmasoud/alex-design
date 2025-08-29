#!/usr/bin/env python
"""
Test script for image optimization system
Run this to test if the optimization is working correctly
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

def test_image_optimization():
    """Test the image optimization system"""
    print("🧪 Testing Image Optimization System")
    print("=" * 50)
    
    # Test project optimization
    print("\n📁 Testing Project Image Optimization:")
    projects = Project.objects.all()[:3]  # Test first 3 projects
    
    for project in projects:
        print(f"\n  Project: {project.title}")
        if project.image:
            print(f"    Main image: {project.image.name}")
            
            # Test optimization
            try:
                ImageOptimizer.optimize_project_images(project)
                print("    ✅ Optimization completed successfully")
                
                # Test getting optimized URLs
                optimized_url = project.get_optimized_image_url('medium', 'webp')
                if optimized_url:
                    print(f"    ✅ Optimized URL: {optimized_url}")
                else:
                    print("    ⚠️  No optimized URL found")
                    
            except Exception as e:
                print(f"    ❌ Optimization failed: {str(e)}")
        else:
            print("    ⚠️  No main image")
        
        # Test album images
        album_count = project.album_images.count()
        if album_count > 0:
            print(f"    Album images: {album_count}")
            try:
                optimized_urls = project.get_optimized_album_image_urls('medium', 'webp')
                print(f"    ✅ Album optimization: {len(optimized_urls)} optimized images")
            except Exception as e:
                print(f"    ❌ Album optimization failed: {str(e)}")
    
    # Test service optimization
    print("\n🔧 Testing Service Image Optimization:")
    services = Service.objects.all()[:3]  # Test first 3 services
    
    for service in services:
        print(f"\n  Service: {service.name}")
        if service.icon:
            print(f"    Icon: {service.icon.name}")
            
            # Test optimization
            try:
                ImageOptimizer.optimize_service_images(service)
                print("    ✅ Optimization completed successfully")
                
                # Test getting optimized URLs
                optimized_url = service.get_optimized_icon_url('medium', 'webp')
                if optimized_url:
                    print(f"    ✅ Optimized URL: {optimized_url}")
                else:
                    print("    ⚠️  No optimized URL found")
                    
            except Exception as e:
                print(f"    ❌ Optimization failed: {str(e)}")
        else:
            print("    ⚠️  No icon")
        
        # Test album images
        album_count = service.album_images.count()
        if album_count > 0:
            print(f"    Album images: {album_count}")
            try:
                optimized_urls = service.get_optimized_album_image_urls('medium', 'webp')
                print(f"    ✅ Album optimization: {len(optimized_urls)} optimized images")
            except Exception as e:
                print(f"    ❌ Album optimization failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Image optimization test completed!")

if __name__ == "__main__":
    test_image_optimization()
