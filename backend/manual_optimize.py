#!/usr/bin/env python
"""
Manual Image Optimization Script
Run this to manually optimize images for specific projects or services
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

def manual_optimize_project(project_id):
    """Manually optimize images for a specific project"""
    try:
        project = Project.objects.get(id=project_id)
        print(f"🖼️  Optimizing images for project: {project.title}")
        
        # Optimize images
        ImageOptimizer.optimize_project_images(project)
        print(f"✅ Successfully optimized images for project: {project.title}")
        
        # Check if optimization worked
        if project.image:
            optimized_url = project.get_optimized_image_url('medium', 'webp')
            if optimized_url:
                print(f"✅ Optimized main image available: {optimized_url}")
            else:
                print("⚠️  Main image optimization may have failed")
        
        return True
        
    except Project.DoesNotExist:
        print(f"❌ Project with ID {project_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error optimizing project {project_id}: {str(e)}")
        return False

def manual_optimize_service(service_id):
    """Manually optimize images for a specific service"""
    try:
        service = Service.objects.get(id=service_id)
        print(f"🖼️  Optimizing images for service: {service.name}")
        
        # Optimize images
        ImageOptimizer.optimize_service_images(service)
        print(f"✅ Successfully optimized images for service: {service.name}")
        
        # Check if optimization worked
        if service.icon:
            optimized_url = service.get_optimized_icon_url('medium', 'webp')
            if optimized_url:
                print(f"✅ Optimized icon available: {optimized_url}")
            else:
                print("⚠️  Icon optimization may have failed")
        
        return True
        
    except Service.DoesNotExist:
        print(f"❌ Service with ID {service_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error optimizing service {service_id}: {str(e)}")
        return False

def list_projects():
    """List all projects with their IDs"""
    print("\n📁 Available Projects:")
    print("-" * 40)
    projects = Project.objects.all()
    for project in projects:
        status = "🖼️" if project.image else "❌"
        print(f"{status} ID: {project.id} - {project.title}")
    return projects

def list_services():
    """List all services with their IDs"""
    print("\n🔧 Available Services:")
    print("-" * 40)
    services = Service.objects.all()
    for service in services:
        status = "🖼️" if service.icon else "❌"
        print(f"{status} ID: {service.id} - {service.name}")
    return services

def main():
    """Main function to run manual optimization"""
    print("🖼️  Manual Image Optimization Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all projects")
        print("2. List all services")
        print("3. Optimize specific project")
        print("4. Optimize specific service")
        print("5. Optimize all projects")
        print("6. Optimize all services")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            list_projects()
            
        elif choice == "2":
            list_services()
            
        elif choice == "3":
            try:
                project_id = int(input("Enter project ID: "))
                manual_optimize_project(project_id)
            except ValueError:
                print("❌ Please enter a valid project ID")
                
        elif choice == "4":
            try:
                service_id = int(input("Enter service ID: "))
                manual_optimize_service(service_id)
            except ValueError:
                print("❌ Please enter a valid service ID")
                
        elif choice == "5":
            print("🖼️  Optimizing all projects...")
            projects = Project.objects.all()
            for project in projects:
                if project.image:
                    print(f"  - Optimizing {project.title}...")
                    manual_optimize_project(project.id)
            print("✅ All projects optimized!")
            
        elif choice == "6":
            print("🖼️  Optimizing all services...")
            services = Service.objects.all()
            for service in services:
                if service.icon:
                    print(f"  - Optimizing {service.name}...")
                    manual_optimize_service(service.id)
            print("✅ All services optimized!")
            
        elif choice == "7":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()
