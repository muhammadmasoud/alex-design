"""
Management command to populate optimized image paths from existing .webp files
This command scans the media folders to find existing optimized images and updates the database
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
from portfolio.models import Project, Service, ProjectImage, ServiceImage


class Command(BaseCommand):
    help = 'Populate optimized image paths from existing .webp files in media folders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if paths already exist',
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
        self.stdout.write(self.style.SUCCESS('Starting to populate optimized image paths from existing files...'))
        
        force = options['force']
        project_id = options.get('project')
        service_id = options.get('service')
        
        if project_id:
            self.populate_project_optimized_paths(project_id, force)
        elif service_id:
            self.populate_service_optimized_paths(service_id, force)
        else:
            self.populate_all_optimized_paths(force)
        
        self.stdout.write(self.style.SUCCESS('Finished populating optimized image paths!'))

    def populate_all_optimized_paths(self, force):
        """Populate all project and service optimized paths"""
        # Update projects
        projects = Project.objects.all()
        self.stdout.write(f'Populating {projects.count()} projects...')
        
        for project in projects:
            self.populate_project_optimized_paths(project.id, force)
        
        # Update services
        services = Service.objects.all()
        self.stdout.write(f'Populating {services.count()} services...')
        
        for service in services:
            self.populate_service_optimized_paths(service.id, force)

    def populate_project_optimized_paths(self, project_id, force):
        """Populate optimized paths for a specific project"""
        try:
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Populating project: {project.title}')
            
            # Check if optimized images exist
            if not force and project.optimized_image:
                self.stdout.write(f'  Project {project.title} already has optimized paths, skipping...')
                return
            
            # Get project folder path
            from django.utils.text import slugify
            project_name = slugify(project.title)[:50]
            project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', project_name)
            
            if not os.path.exists(project_folder):
                self.stdout.write(f'  Project folder not found: {project_folder}')
                return
            
            # Check for main image optimization
            if project.image:
                main_image_name = os.path.splitext(os.path.basename(project.image.name))[0]
                webp_folder = os.path.join(project_folder, 'webp')
                
                if os.path.exists(webp_folder):
                    # Look for optimized main image
                    main_webp_path = os.path.join(webp_folder, f"{main_image_name}.webp")
                    if os.path.exists(main_webp_path):
                        # Update project with optimized paths
                        self._update_project_paths_from_files(project, webp_folder, main_image_name)
                        self.stdout.write(f'  ✓ Updated project {project.title} with optimized paths')
                    else:
                        self.stdout.write(f'  ✗ No optimized main image found for {project.title}')
                else:
                    self.stdout.write(f'  ✗ No webp folder found for project {project.title}')
            
            # Check for album images
            for album_image in project.album_images.all():
                if album_image.image:
                    album_image_name = os.path.splitext(os.path.basename(album_image.image.name))[0]
                    webp_album_folder = os.path.join(project_folder, 'webp', 'album')
                    
                    if os.path.exists(webp_album_folder):
                        # Look for optimized album image
                        album_webp_path = os.path.join(webp_album_folder, f"{album_image_name}.webp")
                        if os.path.exists(album_webp_path):
                            # Update album image with optimized paths
                            self._update_project_album_paths_from_files(album_image, webp_album_folder, album_image_name)
                            self.stdout.write(f'  ✓ Updated album image {album_image.id} with optimized paths')
                        else:
                            self.stdout.write(f'  ✗ No optimized album image found for {album_image.id}')
                    else:
                        self.stdout.write(f'  ✗ No webp/album folder found for project {project.title}')
                
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project with ID {project_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating project {project_id}: {str(e)}'))

    def populate_service_optimized_paths(self, service_id, force):
        """Populate optimized paths for a specific service"""
        try:
            service = Service.objects.get(id=service_id)
            self.stdout.write(f'Populating service: {service.name}')
            
            # Check if optimized images exist
            if not force and service.optimized_icon:
                self.stdout.write(f'  Service {service.name} already has optimized paths, skipping...')
                return
            
            # Get service folder path
            from django.utils.text import slugify
            service_name = slugify(service.name)[:50]
            service_folder = os.path.join(settings.MEDIA_ROOT, 'services', service_name)
            
            if not os.path.exists(service_folder):
                self.stdout.write(f'  Service folder not found: {service_folder}')
                return
            
            # Check for icon optimization
            if service.icon:
                icon_name = os.path.splitext(os.path.basename(service.icon.name))[0]
                webp_folder = os.path.join(service_folder, 'webp')
                
                if os.path.exists(webp_folder):
                    # Look for optimized icon
                    icon_webp_path = os.path.join(webp_folder, f"{icon_name}.webp")
                    if os.path.exists(icon_webp_path):
                        # Update service with optimized paths
                        self._update_service_paths_from_files(service, webp_folder, icon_name)
                        self.stdout.write(f'  ✓ Updated service {service.name} with optimized paths')
                    else:
                        self.stdout.write(f'  ✗ No optimized icon found for {service.name}')
                else:
                    self.stdout.write(f'  ✗ No webp folder found for service {service.name}')
            
            # Check for album images
            for album_image in service.album_images.all():
                if album_image.image:
                    album_image_name = os.path.splitext(os.path.basename(album_image.image.name))[0]
                    webp_album_folder = os.path.join(service_folder, 'webp', 'album')
                    
                    if os.path.exists(webp_album_folder):
                        # Look for optimized album image
                        album_webp_path = os.path.join(webp_album_folder, f"{album_image_name}.webp")
                        if os.path.exists(album_webp_path):
                            # Update album image with optimized paths
                            self._update_service_album_paths_from_files(album_image, webp_album_folder, album_image_name)
                            self.stdout.write(f'  ✓ Updated service album image {album_image.id} with optimized paths')
                        else:
                            self.stdout.write(f'  ✗ No optimized service album image found for {album_image.id}')
                    else:
                        self.stdout.write(f'  ✗ No webp/album folder found for service {service.name}')
                
        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Service with ID {service_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating service {service_id}: {str(e)}'))

    def _update_project_paths_from_files(self, project, webp_folder, base_name):
        """Update project optimized paths from existing files"""
        try:
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the project model fields
            project.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            project.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            project.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            project.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_project_images_on_save
            post_save.disconnect(optimize_project_images_on_save, sender=type(project))
            
            try:
                project.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_project_images_on_save, sender=type(project))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating project paths: {str(e)}'))

    def _update_project_album_paths_from_files(self, album_image, webp_folder, base_name):
        """Update project album image optimized paths from existing files"""
        try:
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the album image model fields
            album_image.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            album_image.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            album_image.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            album_image.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_project_album_image_on_save
            post_save.disconnect(optimize_project_album_image_on_save, sender=type(album_image))
            
            try:
                album_image.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_project_album_image_on_save, sender=type(album_image))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating project album paths: {str(e)}'))

    def _update_service_paths_from_files(self, service, webp_folder, base_name):
        """Update service optimized paths from existing files"""
        try:
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the service model fields
            service.optimized_icon = f"{webp_folder_rel}/{base_name}.webp"
            service.optimized_icon_small = f"{webp_folder_rel}/{base_name}_small.webp"
            service.optimized_icon_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            service.optimized_icon_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_service_images_on_save
            post_save.disconnect(optimize_service_images_on_save, sender=type(service))
            
            try:
                service.save(update_fields=[
                    'optimized_icon', 'optimized_icon_small', 
                    'optimized_icon_medium', 'optimized_icon_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_service_images_on_save, sender=type(service))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating service paths: {str(e)}'))

    def _update_service_album_paths_from_files(self, album_image, webp_folder, base_name):
        """Update service album image optimized paths from existing files"""
        try:
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the album image model fields
            album_image.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            album_image.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            album_image.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            album_image.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_service_album_image_on_save
            post_save.disconnect(optimize_service_album_image_on_save, sender=type(album_image))
            
            try:
                album_image.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_service_album_image_on_save, sender=type(album_image))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating service album paths: {str(e)}'))
