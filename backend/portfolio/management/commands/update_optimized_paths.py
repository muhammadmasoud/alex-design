"""
Management command to update existing images with their optimized paths
This command will populate the new optimized_image fields for existing images
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
from portfolio.models import Project, Service, ProjectImage, ServiceImage
from portfolio.image_optimizer import ImageOptimizer


class Command(BaseCommand):
    help = 'Update existing images with their optimized paths'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of all images',
        )
        parser.add_argument(
            '--project',
            type=int,
            help='Update only a specific project by ID',
        )
        parser.add_argument(
            '--service',
            type=int,
            help='Update only a specific service by ID',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to update optimized image paths...'))
        
        force = options['force']
        project_id = options.get('project')
        service_id = options.get('service')
        
        if project_id:
            self.update_project_images(project_id, force)
        elif service_id:
            self.update_service_images(service_id, force)
        else:
            self.update_all_images(force)
        
        self.stdout.write(self.style.SUCCESS('Finished updating optimized image paths!'))

    def update_all_images(self, force):
        """Update all project and service images"""
        # Update projects
        projects = Project.objects.all()
        self.stdout.write(f'Updating {projects.count()} projects...')
        
        for project in projects:
            self.update_project_images(project.id, force)
        
        # Update services
        services = Service.objects.all()
        self.stdout.write(f'Updating {services.count()} services...')
        
        for service in services:
            self.update_service_images(service.id, force)

    def update_project_images(self, project_id, force):
        """Update images for a specific project"""
        try:
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Updating project: {project.title}')
            
            # Check if optimized images exist
            if not force and project.optimized_image:
                self.stdout.write(f'  Project {project.title} already has optimized paths, skipping...')
                return
            
            # Re-optimize project images
            ImageOptimizer.optimize_project_images(project)
            
            # Refresh from database
            project.refresh_from_db()
            
            if project.optimized_image:
                self.stdout.write(f'  ✓ Updated project {project.title} with optimized paths')
            else:
                self.stdout.write(f'  ✗ Failed to update project {project.title}')
                
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project with ID {project_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating project {project_id}: {str(e)}'))

    def update_service_images(self, service_id, force):
        """Update images for a specific service"""
        try:
            service = Service.objects.get(id=service_id)
            self.stdout.write(f'Updating service: {service.name}')
            
            # Check if optimized images exist
            if not force and service.optimized_icon:
                self.stdout.write(f'  Service {service.name} already has optimized paths, skipping...')
                return
            
            # Re-optimize service images
            ImageOptimizer.optimize_service_images(service)
            
            # Refresh from database
            service.refresh_from_db()
            
            if service.optimized_icon:
                self.stdout.write(f'  ✓ Updated service {service.name} with optimized paths')
            else:
                self.stdout.write(f'  ✗ Failed to update service {service.name}')
                
        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Service with ID {service_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating service {service_id}: {str(e)}'))

    def check_optimized_files(self):
        """Check which optimized files exist on disk"""
        self.stdout.write('Checking existing optimized files...')
        
        media_root = settings.MEDIA_ROOT
        projects_dir = os.path.join(media_root, 'projects')
        services_dir = os.path.join(media_root, 'services')
        
        if os.path.exists(projects_dir):
            project_folders = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
            self.stdout.write(f'Found {len(project_folders)} project folders')
            
            for folder in project_folders:
                webp_dir = os.path.join(projects_dir, folder, 'webp')
                if os.path.exists(webp_dir):
                    webp_files = [f for f in os.listdir(webp_dir) if f.endswith('.webp')]
                    self.stdout.write(f'  {folder}: {len(webp_files)} .webp files')
        
        if os.path.exists(services_dir):
            service_folders = [d for d in os.listdir(services_dir) if os.path.isdir(os.path.join(services_dir, d))]
            self.stdout.write(f'Found {len(service_folders)} service folders')
            
            for folder in service_folders:
                webp_dir = os.path.join(services_dir, folder, 'webp')
                if os.path.exists(webp_dir):
                    webp_files = [f for f in os.listdir(webp_dir) if f.endswith('.webp')]
                    self.stdout.write(f'  {folder}: {len(webp_files)} .webp files')
