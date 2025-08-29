"""
Django management command to optimize all existing images
Usage: python manage.py optimize_images
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.models import Project, Service
from portfolio.image_optimizer import ImageOptimizer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimize all existing images in the system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--projects-only',
            action='store_true',
            help='Only optimize project images',
        )
        parser.add_argument(
            '--services-only',
            action='store_true',
            help='Only optimize service images',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of already optimized images',
        )
        parser.add_argument(
            '--project-id',
            type=int,
            help='Optimize specific project by ID',
        )
        parser.add_argument(
            '--service-id',
            type=int,
            help='Optimize specific service by ID',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image optimization...'))
        
        try:
            # Handle specific project/service optimization
            if options['project_id']:
                self.optimize_specific_project(options['project_id'], options['force'])
                return
            
            if options['service_id']:
                self.optimize_specific_service(options['service_id'], options['force'])
                return
            
            # Handle bulk optimization
            if not options['services_only']:
                self.optimize_projects(options['force'])
            
            if not options['projects_only']:
                self.optimize_services(options['force'])
            
            self.stdout.write(self.style.SUCCESS('Image optimization completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during optimization: {str(e)}'))
            logger.error(f'Error during image optimization: {str(e)}')
    
    def optimize_projects(self, force=False):
        """Optimize all project images"""
        projects = Project.objects.all()
        total_projects = projects.count()
        
        if total_projects == 0:
            self.stdout.write('No projects found to optimize.')
            return
        
        self.stdout.write(f'Found {total_projects} projects to optimize...')
        
        for i, project in enumerate(projects, 1):
            try:
                self.stdout.write(f'[{i}/{total_projects}] Optimizing project: {project.title}')
                
                # Check if optimization is needed
                if not force and self._is_project_optimized(project):
                    self.stdout.write(f'  - Project {project.title} already optimized, skipping...')
                    continue
                
                # Optimize images
                ImageOptimizer.optimize_project_images(project)
                self.stdout.write(f'  - Successfully optimized project: {project.title}')
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  - Failed to optimize project {project.title}: {str(e)}'))
                logger.error(f'Failed to optimize project {project.title}: {str(e)}')
    
    def optimize_services(self, force=False):
        """Optimize all service images"""
        services = Service.objects.all()
        total_services = services.count()
        
        if total_services == 0:
            self.stdout.write('No services found to optimize.')
            return
        
        self.stdout.write(f'Found {total_services} services to optimize...')
        
        for i, service in enumerate(services, 1):
            try:
                self.stdout.write(f'[{i}/{total_services}] Optimizing service: {service.name}')
                
                # Check if optimization is needed
                if not force and self._is_service_optimized(service):
                    self.stdout.write(f'  - Service {service.name} already optimized, skipping...')
                    continue
                
                # Optimize images
                ImageOptimizer.optimize_service_images(service)
                self.stdout.write(f'  - Successfully optimized service: {service.name}')
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  - Failed to optimize service {service.name}: {str(e)}'))
                logger.error(f'Failed to optimize service {service.name}: {str(e)}')
    
    def _is_project_optimized(self, project):
        """Check if a project already has optimized images"""
        import os
        from django.conf import settings
        
        if not project.image:
            return True  # No image to optimize
        
        project_folder = ImageOptimizer._get_project_folder(project)
        webp_folder = os.path.join(project_folder, 'webp')
        
        # Check if webp folder exists and has content
        if not os.path.exists(webp_folder):
            return False
        
        # Check if main image is optimized
        main_image_name = os.path.splitext(os.path.basename(project.image.path))[0]
        main_webp_path = os.path.join(webp_folder, f"{main_image_name}.webp")
        
        if not os.path.exists(main_webp_path):
            return False
        
        # Check if album images are optimized
        album_webp_folder = os.path.join(webp_folder, 'album')
        if project.album_images.exists() and not os.path.exists(album_webp_folder):
            return False
        
        return True
    
    def optimize_specific_project(self, project_id, force=False):
        """Optimize a specific project by ID"""
        try:
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Optimizing project: {project.title}')
            
            # Check if optimization is needed
            if not force and self._is_project_optimized(project):
                self.stdout.write(f'  - Project {project.title} already optimized, skipping...')
                return
            
            # Optimize images
            ImageOptimizer.optimize_project_images(project)
            self.stdout.write(f'  - Successfully optimized project: {project.title}')
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project with ID {project_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  - Failed to optimize project {project_id}: {str(e)}'))
            logger.error(f'Failed to optimize project {project_id}: {str(e)}')
    
    def optimize_specific_service(self, service_id, force=False):
        """Optimize a specific service by ID"""
        try:
            service = Service.objects.get(id=service_id)
            self.stdout.write(f'Optimizing service: {service.name}')
            
            # Check if optimization is needed
            if not force and self._is_service_optimized(service):
                self.stdout.write(f'  - Service {service.name} already optimized, skipping...')
                return
            
            # Optimize images
            ImageOptimizer.optimize_service_images(service)
            self.stdout.write(f'  - Successfully optimized service: {service.name}')
            
        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Service with ID {service_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  - Failed to optimize service {service_id}: {str(e)}'))
            logger.error(f'Failed to optimize service {service_id}: {str(e)}')
    
    def _is_service_optimized(self, service):
        """Check if a service already has optimized images"""
        import os
        from django.conf import settings
        
        if not service.icon:
            return True  # No icon to optimize
        
        service_folder = ImageOptimizer._get_service_folder(service)
        webp_folder = os.path.join(service_folder, 'webp')
        
        # Check if webp folder exists and has content
        if not os.path.exists(webp_folder):
            return False
        
        # Check if icon is optimized
        icon_name = os.path.splitext(os.path.basename(service.icon.path))[0]
        icon_webp_path = os.path.join(webp_folder, f"{icon_name}.webp")
        
        if not os.path.exists(icon_webp_path):
            return False
        
        # Check if album images are optimized
        album_webp_folder = os.path.join(webp_folder, 'album')
        if service.album_images.exists() and not os.path.exists(album_webp_folder):
            return False
        
        return True
