#!/usr/bin/env python
"""
Debug script to check the async optimization system
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.portfolio.async_optimizer import AsyncImageOptimizer
from backend.portfolio.models import Project
import time

def check_optimization_system():
    print("=== Debugging Async Optimization System ===")
    
    # Check queue status
    status = AsyncImageOptimizer.get_queue_status()
    print(f"Queue Status: {status}")
    
    # Check if directories exist
    AsyncImageOptimizer._ensure_dirs()
    print(f"Queue Directory: {AsyncImageOptimizer.QUEUE_DIR}")
    print(f"Processing Directory: {AsyncImageOptimizer.PROCESSING_DIR}")
    
    # List any existing queue files
    queue_files = list(AsyncImageOptimizer.QUEUE_DIR.glob('*.json'))
    print(f"Queued tasks: {len(queue_files)}")
    for f in queue_files:
        print(f"  - {f.name}")
    
    # List any processing files
    processing_files = list(AsyncImageOptimizer.PROCESSING_DIR.glob('*.json'))
    print(f"Processing tasks: {len(processing_files)}")
    for f in processing_files:
        print(f"  - {f.name}")
    
    # Test queuing a project
    projects = Project.objects.all()[:1]
    if projects:
        project = projects[0]
        print(f"\nTesting optimization queue for project: {project.title}")
        
        try:
            AsyncImageOptimizer.queue_project_optimization(
                project_id=project.id,
                operation_type='test'
            )
            print("✓ Successfully queued optimization")
            
            # Wait a moment and check again
            time.sleep(2)
            new_status = AsyncImageOptimizer.get_queue_status()
            print(f"New Queue Status: {new_status}")
            
        except Exception as e:
            print(f"✗ Failed to queue optimization: {e}")
    else:
        print("No projects found to test with")

if __name__ == "__main__":
    check_optimization_system()
