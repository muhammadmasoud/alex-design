#!/usr/bin/env python3
"""
Test script to verify that serialization fixes work correctly.
Run this script to test the serializers without making HTTP requests.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectImage, Service, ServiceImage
from portfolio.serializers import (
    ProjectImageSerializer, ServiceImageSerializer, 
    ProjectSerializer, ServiceSerializer
)
from django.test import RequestFactory

def test_project_image_serializer():
    """Test ProjectImageSerializer with various scenarios"""
    print("Testing ProjectImageSerializer...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/test/')
    
    try:
        # Test with a project that has images
        projects = Project.objects.all()[:1]
        if projects:
            project = projects[0]
            images = project.album_images.all()[:1]
            
            if images:
                image = images[0]
                print(f"Testing serialization of image: {image.id}")
                
                # Test serialization
                serializer = ProjectImageSerializer(image, context={'request': request})
                data = serializer.data
                print(f"✓ Serialization successful: {len(data)} fields")
                
                # Test many=True
                serializer_many = ProjectImageSerializer(images, many=True, context={'request': request})
                data_many = serializer_many.data
                print(f"✓ Many serialization successful: {len(data_many)} images")
            else:
                print("No images found for testing")
        else:
            print("No projects found for testing")
            
    except Exception as e:
        print(f"✗ ProjectImageSerializer test failed: {e}")
        import traceback
        traceback.print_exc()

def test_service_image_serializer():
    """Test ServiceImageSerializer with various scenarios"""
    print("\nTesting ServiceImageSerializer...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/test/')
    
    try:
        # Test with a service that has images
        services = Service.objects.all()[:1]
        if services:
            service = services[0]
            images = service.album_images.all()[:1]
            
            if images:
                image = images[0]
                print(f"Testing serialization of image: {image.id}")
                
                # Test serialization
                serializer = ServiceImageSerializer(image, context={'request': request})
                data = serializer.data
                print(f"✓ Serialization successful: {len(data)} fields")
                
                # Test many=True
                serializer_many = ServiceImageSerializer(images, many=True, context={'request': request})
                data_many = serializer_many.data
                print(f"✓ Many serialization successful: {len(data_many)} images")
            else:
                print("No images found for testing")
        else:
            print("No services found for testing")
            
    except Exception as e:
        print(f"✗ ServiceImageSerializer test failed: {e}")
        import traceback
        traceback.print_exc()

def test_project_serializer():
    """Test ProjectSerializer with various scenarios"""
    print("\nTesting ProjectSerializer...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/test/')
    
    try:
        # Test with a project
        projects = Project.objects.all()[:1]
        if projects:
            project = projects[0]
            print(f"Testing serialization of project: {project.id}")
            
            # Test serialization
            serializer = ProjectSerializer(project, context={'request': request})
            data = serializer.data
            print(f"✓ Serialization successful: {len(data)} fields")
            
            # Test many=True
            serializer_many = ProjectSerializer(projects, many=True, context={'request': request})
            data_many = serializer_many.data
            print(f"✓ Many serialization successful: {len(data_many)} projects")
        else:
            print("No projects found for testing")
            
    except Exception as e:
        print(f"✗ ProjectSerializer test failed: {e}")
        import traceback
        traceback.print_exc()

def test_service_serializer():
    """Test ServiceSerializer with various scenarios"""
    print("\nTesting ServiceSerializer...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/test/')
    
    try:
        # Test with a service
        services = Service.objects.all()[:1]
        if services:
            service = services[0]
            print(f"Testing serialization of service: {service.id}")
            
            # Test serialization
            serializer = ServiceSerializer(service, context={'request': request})
            data = serializer.data
            print(f"✓ Serialization successful: {len(data)} fields")
            
            # Test many=True
            serializer_many = ServiceSerializer(services, many=True, context={'request': request})
            data_many = serializer_many.data
            print(f"✓ Many serialization successful: {len(data_many)} services")
        else:
            print("No services found for testing")
            
    except Exception as e:
        print(f"✗ ServiceSerializer test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("Starting serialization tests...")
    print("=" * 50)
    
    try:
        test_project_image_serializer()
        test_service_image_serializer()
        test_project_serializer()
        test_service_serializer()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
