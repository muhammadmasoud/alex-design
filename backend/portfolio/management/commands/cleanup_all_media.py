import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Clean up all media files since database is empty'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting files',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Starting media cleanup...'))
        
        # Directories to clean
        media_root = settings.MEDIA_ROOT
        old_projects_dir = os.path.join(os.path.dirname(media_root), 'projects')
        
        directories_to_clean = []
        total_size = 0
        file_count = 0
        
        # Check media/projects directory
        projects_media_dir = os.path.join(media_root, 'projects')
        if os.path.exists(projects_media_dir):
            directories_to_clean.append(('media/projects', projects_media_dir))
        
        # Check media/services directory
        services_media_dir = os.path.join(media_root, 'services')
        if os.path.exists(services_media_dir):
            directories_to_clean.append(('media/services', services_media_dir))
        
        # Check old projects directory (not in media)
        if os.path.exists(old_projects_dir):
            directories_to_clean.append(('projects', old_projects_dir))
        
        # Calculate total size and file count
        for name, directory in directories_to_clean:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        pass
        
        if file_count == 0:
            self.stdout.write(self.style.SUCCESS('No media files found to clean!'))
            return
        
        # Convert bytes to MB
        total_size_mb = total_size / (1024 * 1024)
        
        self.stdout.write(f'Found {file_count} files in {len(directories_to_clean)} directories')
        self.stdout.write(f'Total size: {total_size_mb:.2f} MB')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n--- DRY RUN MODE - Directories that would be cleaned: ---'))
            for name, directory in directories_to_clean:
                rel_path = os.path.relpath(directory, settings.BASE_DIR)
                dir_size = 0
                dir_files = 0
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            dir_size += os.path.getsize(file_path)
                            dir_files += 1
                        except OSError:
                            pass
                dir_size_mb = dir_size / (1024 * 1024)
                self.stdout.write(f'{rel_path}: {dir_files} files ({dir_size_mb:.2f} MB)')
            return
        
        # Confirmation prompt
        self.stdout.write(self.style.WARNING(f'\nThis will permanently delete all {file_count} media files ({total_size_mb:.2f} MB)'))
        self.stdout.write('Since you mentioned your database is empty, this should be safe.')
        
        response = input('\nAre you sure you want to proceed? (yes/no): ')
        if response.lower() not in ['yes', 'y']:
            self.stdout.write('Cleanup cancelled.')
            return
        
        # Delete the directories
        deleted_size = 0
        deleted_files = 0
        errors = []
        
        for name, directory in directories_to_clean:
            try:
                # Calculate size before deletion
                dir_size = 0
                dir_files = 0
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            dir_size += os.path.getsize(file_path)
                            dir_files += 1
                        except OSError:
                            pass
                
                # Remove the entire directory
                shutil.rmtree(directory)
                deleted_size += dir_size
                deleted_files += dir_files
                
                rel_path = os.path.relpath(directory, settings.BASE_DIR)
                dir_size_mb = dir_size / (1024 * 1024)
                self.stdout.write(f'Deleted directory: {rel_path} ({dir_files} files, {dir_size_mb:.2f} MB)')
                
            except OSError as e:
                errors.append(f'Error deleting {directory}: {e}')
        
        deleted_size_mb = deleted_size / (1024 * 1024)
        
        self.stdout.write(self.style.SUCCESS(f'\nCleanup completed!'))
        self.stdout.write(f'Deleted {deleted_files} files ({deleted_size_mb:.2f} MB)')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\nErrors encountered:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(error))
        
        self.stdout.write(self.style.SUCCESS('\nYour media storage has been cleaned up!'))
        self.stdout.write('The Django signals have been updated to automatically delete files when you delete projects/services in the future.')
