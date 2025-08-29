"""
Django management command to migrate existing projects to the new folder structure.
This command will:
1. Create project-specific folders for each existing project
2. Move existing images to the new folder structure
3. Update database records with new image paths
"""
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from portfolio.models import Project, ProjectImage
import os
import shutil


class Command(BaseCommand):
    help = 'Migrate existing projects to the new folder structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if folders already exist',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Starting project folder migration...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Get all projects
        projects = Project.objects.all()
        self.stdout.write(f'Found {projects.count()} projects to migrate')
        
        migrated_count = 0
        errors = []
        
        for project in projects:
            try:
                self.stdout.write(f'\nProcessing project: {project.title} (ID: {project.pk})')
                
                # Create project folder structure
                project_folder = f"project_{project.pk}"
                project_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder)
                album_path = os.path.join(project_path, 'album')
                
                if not dry_run:
                    # Create directories
                    os.makedirs(project_path, exist_ok=True)
                    os.makedirs(album_path, exist_ok=True)
                    self.stdout.write(f'  ✓ Created folder: {project_folder}')
                else:
                    self.stdout.write(f'  Would create folder: {project_folder}')
                
                # Handle main project image
                if project.image and project.image.name:
                    self.stdout.write(f'  Processing main image: {project.image.name}')
                    
                    # Check if image is already in the correct location
                    if f'projects/{project_folder}/' in project.image.name:
                        self.stdout.write(f'    ✓ Already in correct location')
                    else:
                        # Move main image to new location
                        old_path = project.image.name
                        filename = os.path.basename(old_path)
                        new_path = f"projects/{project_folder}/{filename}"
                        
                        if not dry_run:
                            if default_storage.exists(old_path):
                                # Read and save to new location
                                with default_storage.open(old_path, 'rb') as old_file:
                                    content = old_file.read()
                                
                                new_file = ContentFile(content)
                                default_storage.save(new_path, new_file)
                                
                                # Update the model
                                project.image.name = new_path
                                project.save(update_fields=['image'])
                                
                                # Delete old file
                                default_storage.delete(old_path)
                                
                                self.stdout.write(f'    ✓ Moved to: {new_path}')
                            else:
                                self.stdout.write(f'    ⚠ File not found: {old_path}')
                        else:
                            self.stdout.write(f'    Would move to: {new_path}')
                
                # Handle album images
                album_images = project.album_images.all()
                if album_images:
                    self.stdout.write(f'  Processing {album_images.count()} album images')
                    
                    for album_image in album_images:
                        if album_image.image and album_image.image.name:
                            # Check if image is already in the correct location
                            if f'projects/{project_folder}/album/' in album_image.image.name:
                                self.stdout.write(f'    ✓ Already in correct location: {os.path.basename(album_image.image.name)}')
                            else:
                                # Move album image to new location
                                old_path = album_image.image.name
                                filename = os.path.basename(old_path)
                                new_path = f"projects/{project_folder}/album/{filename}"
                                
                                if not dry_run:
                                    if default_storage.exists(old_path):
                                        # Read and save to new location
                                        with default_storage.open(old_path, 'rb') as old_file:
                                            content = old_file.read()
                                        
                                        new_file = ContentFile(content)
                                        default_storage.save(new_path, new_file)
                                        
                                        # Update the model
                                        album_image.image.name = new_path
                                        album_image.save(update_fields=['image'])
                                        
                                        # Delete old file
                                        default_storage.delete(old_path)
                                        
                                        self.stdout.write(f'    ✓ Moved to: {new_path}')
                                    else:
                                        self.stdout.write(f'    ⚠ File not found: {old_path}')
                                else:
                                    self.stdout.write(f'    Would move to: {new_path}')
                
                migrated_count += 1
                self.stdout.write(f'  ✓ Project {project.title} migrated successfully')
                
            except Exception as e:
                error_msg = f'Error migrating project {project.title}: {str(e)}'
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {error_msg}')
                )
                errors.append(error_msg)
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MIGRATION SUMMARY')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(f'Would migrate: {migrated_count} projects')
        else:
            self.stdout.write(f'Successfully migrated: {migrated_count} projects')
        
        if errors:
            self.stdout.write(f'\nErrors encountered: {len(errors)}')
            for error in errors:
                self.stdout.write(f'  - {error}')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('\nMigration completed successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nDry run completed. No changes were made.')
            )
