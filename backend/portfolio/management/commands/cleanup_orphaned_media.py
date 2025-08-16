import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Project, Service, ProjectImage, ServiceImage


class Command(BaseCommand):
    help = 'Clean up orphaned media files that are not referenced by any database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting files',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Delete files without confirmation prompt',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('Starting orphaned media cleanup...'))
        
        # Get all media file paths that should exist according to the database
        referenced_files = set()
        
        # Project main images
        for project in Project.objects.exclude(image='').exclude(image__isnull=True):
            if project.image and project.image.name:
                referenced_files.add(project.image.path)
        
        # Service main icons
        for service in Service.objects.exclude(icon='').exclude(icon__isnull=True):
            if service.icon and service.icon.name:
                referenced_files.add(service.icon.path)
        
        # Project album images
        for project_image in ProjectImage.objects.exclude(image='').exclude(image__isnull=True):
            if project_image.image and project_image.image.name:
                referenced_files.add(project_image.image.path)
        
        # Service album images
        for service_image in ServiceImage.objects.exclude(image='').exclude(image__isnull=True):
            if service_image.image and service_image.image.name:
                referenced_files.add(service_image.image.path)
        
        self.stdout.write(f'Found {len(referenced_files)} files referenced in database')
        
        # Get all actual files in the media directories
        media_root = settings.MEDIA_ROOT
        orphaned_files = []
        total_size = 0
        
        # Check projects directory
        projects_dir = os.path.join(media_root, 'projects')
        if os.path.exists(projects_dir):
            for root, dirs, files in os.walk(projects_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in referenced_files:
                        orphaned_files.append(file_path)
                        try:
                            total_size += os.path.getsize(file_path)
                        except OSError:
                            pass
        
        # Check services directory
        services_dir = os.path.join(media_root, 'services')
        if os.path.exists(services_dir):
            for root, dirs, files in os.walk(services_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in referenced_files:
                        orphaned_files.append(file_path)
                        try:
                            total_size += os.path.getsize(file_path)
                        except OSError:
                            pass
        
        # Also check the old projects directory (not in media)
        old_projects_dir = os.path.join(os.path.dirname(media_root), 'projects')
        if os.path.exists(old_projects_dir):
            for root, dirs, files in os.walk(old_projects_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    orphaned_files.append(file_path)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        pass
        
        if not orphaned_files:
            self.stdout.write(self.style.SUCCESS('No orphaned files found!'))
            return
        
        # Convert bytes to MB
        total_size_mb = total_size / (1024 * 1024)
        
        self.stdout.write(f'Found {len(orphaned_files)} orphaned files')
        self.stdout.write(f'Total size: {total_size_mb:.2f} MB')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n--- DRY RUN MODE - Files that would be deleted: ---'))
            for file_path in orphaned_files:
                rel_path = os.path.relpath(file_path, settings.BASE_DIR)
                try:
                    size_kb = os.path.getsize(file_path) / 1024
                    self.stdout.write(f'{rel_path} ({size_kb:.1f} KB)')
                except OSError:
                    self.stdout.write(f'{rel_path} (size unknown)')
            return
        
        # Confirmation prompt
        if not force:
            self.stdout.write(self.style.WARNING(f'\nThis will permanently delete {len(orphaned_files)} files ({total_size_mb:.2f} MB)'))
            
            # Show first 10 files as examples
            self.stdout.write('\nFiles to be deleted (showing first 10):')
            for file_path in orphaned_files[:10]:
                rel_path = os.path.relpath(file_path, settings.BASE_DIR)
                self.stdout.write(f'  {rel_path}')
            
            if len(orphaned_files) > 10:
                self.stdout.write(f'  ... and {len(orphaned_files) - 10} more files')
            
            response = input('\nAre you sure you want to proceed? (yes/no): ')
            if response.lower() not in ['yes', 'y']:
                self.stdout.write('Cleanup cancelled.')
                return
        
        # Delete the files
        deleted_count = 0
        deleted_size = 0
        errors = []
        
        for file_path in orphaned_files:
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_count += 1
                deleted_size += file_size
                self.stdout.write(f'Deleted: {os.path.relpath(file_path, settings.BASE_DIR)}')
            except OSError as e:
                errors.append(f'Error deleting {file_path}: {e}')
        
        # Clean up empty directories
        for root_dir in [projects_dir, services_dir, old_projects_dir]:
            if os.path.exists(root_dir):
                self._remove_empty_dirs(root_dir)
        
        deleted_size_mb = deleted_size / (1024 * 1024)
        
        self.stdout.write(self.style.SUCCESS(f'\nCleanup completed!'))
        self.stdout.write(f'Deleted {deleted_count} files ({deleted_size_mb:.2f} MB)')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\nErrors encountered:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(error))

    def _remove_empty_dirs(self, directory):
        """Remove empty directories recursively"""
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Directory is empty
                            os.rmdir(dir_path)
                            self.stdout.write(f'Removed empty directory: {os.path.relpath(dir_path, settings.BASE_DIR)}')
                    except OSError:
                        pass  # Directory not empty or other error
        except OSError:
            pass
