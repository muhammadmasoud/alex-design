#!/usr/bin/env python3
"""
Test script to verify serialization is working correctly
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, ProjectImage, Service, ServiceImage
from portfolio.serializers import ProjectSerializer, ProjectImageSerializer, ServiceSerializer, ServiceImageSerializer
from django.test import RequestFactory

def test_project_serialization():
    """Test project serialization"""
    print("Testing project serialization...")
    
    try:
        # Get a project
        project = Project.objects.first()
        if not project:
            print("No projects found in database")
            return
        
        print(f"Testing serialization for project: {project.title}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Test serializer
        serializer = ProjectSerializer(project, context={'request': request})
        data = serializer.data
        
        print(f"Serialization successful: {len(data)} fields")
        print(f"Project ID: {data.get('id')}")
        print(f"Title: {data.get('title')}")
        print(f"Image: {data.get('image')}")
        print(f"Image URL: {data.get('image_url')}")
        
        return True
        
    except Exception as e:
        print(f"Project serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_image_serialization():
    """Test project image serialization"""
    print("\nTesting project image serialization...")
    
    try:
        # Get a project image
        project_image = ProjectImage.objects.first()
        if not project_image:
            print("No project images found in database")
            return
        
        print(f"Testing serialization for project image: {project_image.id}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Test serializer
        serializer = ProjectImageSerializer(project_image, context={'request': request})
        data = serializer.data
        
        print(f"Serialization successful: {len(data)} fields")
        print(f"Image ID: {data.get('id')}")
        print(f"Image: {data.get('image')}")
        print(f"Image URL: {data.get('image_url')}")
        
        return True
        
    except Exception as e:
        print(f"Project image serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_serialization():
    """Test service serialization"""
    print("\nTesting service serialization...")
    
    try:
        # Get a service
        service = Service.objects.first()
        if not service:
            print("No services found in database")
            return
        
        print(f"Testing serialization for service: {service.name}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Test serializer
        serializer = ServiceSerializer(service, context={'request': request})
        data = serializer.data
        
        print(f"Serialization successful: {len(data)} fields")
        print(f"Service ID: {data.get('id')}")
        print(f"Name: {data.get('name')}")
        print(f"Icon: {data.get('icon')}")
        print(f"Icon URL: {data.get('icon_url')}")
        
        return True
        
    except Exception as e:
        print(f"Service serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_image_serialization():
    """Test service image serialization"""
    print("\nTesting service image serialization...")
    
    try:
        # Get a service image
        service_image = ServiceImage.objects.first()
        if not service_image:
            print("No service images found in database")
            return
        
        print(f"Testing serialization for service image: {service_image.id}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Test serializer
        serializer = ServiceImageSerializer(service_image, context={'request': request})
        data = serializer.data
        
        print(f"Serialization successful: {len(data)} fields")
        print(f"Image ID: {data.get('id')}")
        print(f"Image: {data.get('image')}")
        print(f"Image URL: {data.get('image_url')}")
        
        return True
        
    except Exception as e:
        print(f"Service image serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Starting serialization tests...")
    print("=" * 50)
    
    results = []
    
    # Test project serialization
    results.append(test_project_serialization())
    
    # Test project image serialization
    results.append(test_project_image_serialization())
    
    # Test service serialization
    results.append(test_service_serialization())
    
    # Test service image serialization
    results.append(test_service_image_serialization())
    
    print("\n" + "=" * 50)
    print("Test Results:")
    
    if all(results):
        print("✅ All serialization tests passed!")
    else:
        print("❌ Some serialization tests failed!")
        print("Check the error messages above for details.")
    
    return all(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
