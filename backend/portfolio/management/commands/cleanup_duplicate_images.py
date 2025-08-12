from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from portfolio.models import Project, Service
import os
import re

class Command(BaseCommand):
    help = 'Clean up duplicate images and update model references'

    def handle(self, *args, **options):
        self.stdout.write('Starting image cleanup...')
        
        # Clean up project images
        self.cleanup_project_images()
        
        # Clean up service icons
        self.cleanup_service_icons()
        
        self.stdout.write(self.style.SUCCESS('Image cleanup completed!'))

    def cleanup_project_images(self):
        """Clean up duplicate project images"""
        projects_path = 'projects'
        
        if not default_storage.exists(projects_path):
            self.stdout.write(f"Projects directory {projects_path} does not exist")
            return
        
        # Get all files in projects directory
        _, files = default_storage.listdir(projects_path)
        
        # Group files by base name (without random suffix)
        file_groups = {}
        for filename in files:
            # Extract base name without random suffix
            base_name = re.sub(r'_[a-zA-Z0-9]{7,}\.', '.', filename)
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(filename)
        
        # For each group, keep the newest file and delete others
        for base_name, file_list in file_groups.items():
            if len(file_list) > 1:
                # Sort by modification time (newest first)
                file_list.sort(key=lambda x: default_storage.get_modified_time(f"{projects_path}/{x}"), reverse=True)
                
                # Keep the newest file
                keep_file = file_list[0]
                self.stdout.write(f"Keeping: {keep_file}")
                
                # Delete duplicates
                for duplicate in file_list[1:]:
                    file_path = f"{projects_path}/{duplicate}"
                    self.stdout.write(f"Deleting duplicate: {duplicate}")
                    default_storage.delete(file_path)
                
                # Update any project that references the old files
                for project in Project.objects.all():
                    if project.image and project.image.name in [f"{projects_path}/{f}" for f in file_list[1:]]:
                        project.image.name = f"{projects_path}/{keep_file}"
                        project.save()
                        self.stdout.write(f"Updated project {project.title} image reference")

    def cleanup_service_icons(self):
        """Clean up duplicate service icons"""
        services_path = 'services'
        
        if not default_storage.exists(services_path):
            self.stdout.write(f"Services directory {services_path} does not exist")
            return
        
        # Get all files in services directory
        try:
            _, files = default_storage.listdir(services_path)
        except:
            self.stdout.write("No services directory found")
            return
        
        # Group files by base name (without random suffix)
        file_groups = {}
        for filename in files:
            # Extract base name without random suffix
            base_name = re.sub(r'_[a-zA-Z0-9]{7,}\.', '.', filename)
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(filename)
        
        # For each group, keep the newest file and delete others
        for base_name, file_list in file_groups.items():
            if len(file_list) > 1:
                # Sort by modification time (newest first)
                file_list.sort(key=lambda x: default_storage.get_modified_time(f"{services_path}/{x}"), reverse=True)
                
                # Keep the newest file
                keep_file = file_list[0]
                self.stdout.write(f"Keeping: {keep_file}")
                
                # Delete duplicates
                for duplicate in file_list[1:]:
                    file_path = f"{services_path}/{duplicate}"
                    self.stdout.write(f"Deleting duplicate: {duplicate}")
                    default_storage.delete(file_path)
                
                # Update any service that references the old files
                for service in Service.objects.all():
                    if service.icon and service.icon.name in [f"{services_path}/{f}" for f in file_list[1:]]:
                        service.icon.name = f"{services_path}/{keep_file}"
                        service.save()
                        self.stdout.write(f"Updated service {service.name} icon reference")
