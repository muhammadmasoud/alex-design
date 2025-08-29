from django.core.management.base import BaseCommand
from django.conf import settings
import os
from portfolio.models import Project, ProjectImage
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Test the automatic folder structure creation for projects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-title',
            type=str,
            default='Test Project',
            help='Title for the test project'
        )

    def handle(self, *args, **options):
        project_title = options['project_title']
        
        self.stdout.write(f"Testing folder structure creation for project: {project_title}")
        
        # Check if project folder should exist
        project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', slugify(project_title))
        album_folder = os.path.join(project_folder, 'album')
        
        self.stdout.write(f"Expected project folder: {project_folder}")
        self.stdout.write(f"Expected album folder: {album_folder}")
        
        # Check if folders exist
        if os.path.exists(project_folder):
            self.stdout.write(self.style.SUCCESS(f"✓ Project folder exists: {project_folder}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Project folder does not exist: {project_folder}"))
        
        if os.path.exists(album_folder):
            self.stdout.write(self.style.SUCCESS(f"✓ Album folder exists: {album_folder}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Album folder does not exist: {album_folder}"))
        
        # List contents of projects directory
        projects_dir = os.path.join(settings.MEDIA_ROOT, 'projects')
        if os.path.exists(projects_dir):
            self.stdout.write(f"\nContents of {projects_dir}:")
            for item in os.listdir(projects_dir):
                item_path = os.path.join(projects_dir, item)
                if os.path.isdir(item_path):
                    self.stdout.write(f"  📁 {item}/")
                    # List contents of project folder
                    try:
                        for subitem in os.listdir(item_path):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isdir(subitem_path):
                                self.stdout.write(f"    📁 {subitem}/")
                            else:
                                self.stdout.write(f"    📄 {subitem}")
                    except PermissionError:
                        self.stdout.write(f"    🔒 Permission denied accessing {item}")
                else:
                    self.stdout.write(f"  📄 {item}")
        else:
            self.stdout.write(self.style.ERROR(f"Projects directory does not exist: {projects_dir}"))
        
        self.stdout.write("\nTest completed!")
