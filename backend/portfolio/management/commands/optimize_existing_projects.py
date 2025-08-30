"""
Management command to optimize existing projects that haven't been optimized yet
Usage: python manage.py optimize_existing_projects
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import models
from portfolio.models import Project
from portfolio.image_optimizer import ImageOptimizer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimize images for existing projects that have not been optimized yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of all projects, even if already optimized',
        )
        parser.add_argument(
            '--project-id',
            type=int,
            help='Optimize specific project by ID',
        )

    def handle(self, *args, **options):
        force = options['force']
        project_id = options.get('project_id')
        
        if project_id:
            # Optimize specific project
            try:
                project = Project.objects.get(id=project_id)
                self.optimize_project(project, force=True)
            except Project.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Project with ID {project_id} not found')
                )
                return
        else:
            # Find projects that need optimization
            if force:
                # Re-optimize all projects
                projects = Project.objects.all()
                self.stdout.write(f"Force re-optimizing {projects.count()} projects...")
            else:
                # Only optimize projects without optimized images OR with images but no optimized versions
                projects_with_images = Project.objects.filter(
                    models.Q(image__isnull=False) | 
                    models.Q(album_images__isnull=False)
                ).distinct()
                
                unoptimized_projects = []
                for project in projects_with_images:
                    # Check if project needs optimization
                    needs_optimization = False
                    
                    # Check main image optimization
                    if project.image and not project.optimized_image:
                        needs_optimization = True
                    
                    # Check if any album images exist but aren't optimized
                    if project.album_images.exists():
                        unoptimized_album_images = project.album_images.filter(
                            optimized_image__isnull=True
                        )
                        if unoptimized_album_images.exists():
                            needs_optimization = True
                    
                    if needs_optimization:
                        unoptimized_projects.append(project)
                
                projects = unoptimized_projects
                self.stdout.write(f"Found {len(projects)} projects that need optimization...")

            if not projects:
                self.stdout.write(
                    self.style.SUCCESS('No projects need optimization!')
                )
                return

            # Optimize each project
            optimized_count = 0
            failed_count = 0
            
            for project in projects:
                success = self.optimize_project(project, force)
                if success:
                    optimized_count += 1
                else:
                    failed_count += 1

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'Optimization complete: {optimized_count} successful, {failed_count} failed'
                )
            )

    def optimize_project(self, project, force=False):
        """Optimize a single project"""
        try:
            self.stdout.write(f"Optimizing project: {project.title}")
            
            # Check if project has any images
            has_main_image = bool(project.image)
            has_album_images = project.album_images.exists()
            
            if not has_main_image and not has_album_images:
                self.stdout.write(
                    self.style.WARNING(f"  Skipping {project.title} - no images found")
                )
                return True
            
            # Use the ImageOptimizer
            ImageOptimizer.optimize_project_images(project)
            
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Successfully optimized {project.title}")
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Failed to optimize {project.title}: {str(e)}")
            )
            logger.error(f"Failed to optimize project {project.title}: {str(e)}")
            return False
