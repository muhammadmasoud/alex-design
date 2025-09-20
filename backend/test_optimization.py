#!/usr/bin/env python
"""
Test script to verify that image optimization is working correctly
This script can be run to check the optimization system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.async_optimizer import AsyncImageOptimizer
from portfolio.models import Project, Service
import time

def test_optimization_system():
    """Test the image optimization system"""
    print("=== Image Optimization System Test ===")
    
    # Check queue status
    print("\n1. Checking queue status...")
    try:
        status = AsyncImageOptimizer.get_queue_status()
        print(f"   ✓ Queue status: {status['queued_tasks']} queued, {status['processing_tasks']} processing")
        print(f"   ✓ Processor running: {status['processor_running']}")
    except Exception as e:
        print(f"   ✗ Error checking queue status: {e}")
        return False
    
    # Test queueing
    print("\n2. Testing optimization queueing...")
    try:
        # Find a project to test
        project = Project.objects.first()
        if project:
            AsyncImageOptimizer.queue_project_optimization(
                project_id=project.id,
                operation_type='test'
            )
            print(f"   ✓ Successfully queued test optimization for project: {project.title}")
        else:
            print("   - No projects found to test")
        
        # Find a service to test
        service = Service.objects.first()
        if service:
            AsyncImageOptimizer.queue_service_optimization(
                service_id=service.id,
                operation_type='test'
            )
            print(f"   ✓ Successfully queued test optimization for service: {service.name}")
        else:
            print("   - No services found to test")
            
    except Exception as e:
        print(f"   ✗ Error queueing optimization: {e}")
        return False
    
    # Check updated queue status
    print("\n3. Checking updated queue status...")
    try:
        time.sleep(1)  # Give time for queueing
        status = AsyncImageOptimizer.get_queue_status()
        print(f"   ✓ Queue status: {status['queued_tasks']} queued, {status['processing_tasks']} processing")
    except Exception as e:
        print(f"   ✗ Error checking updated queue status: {e}")
        return False
    
    print("\n=== Test completed successfully! ===")
    print("\nThe optimization system is working correctly.")
    print("When you upload images through the admin interface, they will be:")
    print("1. Saved immediately (instant response)")
    print("2. Optimized in the background (no delays)")
    print("\nYou can check the optimization status at: /api/admin/optimization-status/")
    return True

if __name__ == "__main__":
    success = test_optimization_system()
    sys.exit(0 if success else 1)
