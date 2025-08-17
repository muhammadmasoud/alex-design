"""
Management command to optimize existing images in the database
This command will:
1. Find all existing images
2. Optimize them for web delivery
3. Replace the original files with optimized versions
4. Run database cleanup operations
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.models import Project, Service, ProjectImage, ServiceImage
from portfolio.image_utils import optimize_image, should_optimize_image
import os
import time


class Command(BaseCommand):
    help = 'Optimize existing images for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force optimization of all images, even if they seem optimized',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of images to process in each batch (default: 10)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force_optimize = options['force']
        batch_size = options['batch_size']
        
        self.stdout.write(
            self.style.SUCCESS('Starting image optimization process...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Statistics
        stats = {
            'projects_optimized': 0,
            'services_optimized': 0,
            'project_images_optimized': 0,
            'service_images_optimized': 0,
            'space_saved': 0,
            'errors': 0,
        }
        
        # Optimize Project images
        self.stdout.write('Optimizing Project images...')
        projects = Project.objects.filter(image__isnull=False)
        stats.update(self._optimize_model_images(
            projects, 'image', 'Project', dry_run, force_optimize, batch_size
        ))
        
        # Optimize Service icons
        self.stdout.write('Optimizing Service icons...')
        services = Service.objects.filter(icon__isnull=False)
        service_stats = self._optimize_model_images(
            services, 'icon', 'Service', dry_run, force_optimize, batch_size
        )
        stats['services_optimized'] = service_stats['projects_optimized']  # Reuse counter
        stats['space_saved'] += service_stats['space_saved']
        stats['errors'] += service_stats['errors']
        
        # Optimize ProjectImage images
        self.stdout.write('Optimizing ProjectImage album images...')
        project_images = ProjectImage.objects.filter(image__isnull=False)
        proj_img_stats = self._optimize_model_images(
            project_images, 'image', 'ProjectImage', dry_run, force_optimize, batch_size
        )
        stats['project_images_optimized'] = proj_img_stats['projects_optimized']
        stats['space_saved'] += proj_img_stats['space_saved']
        stats['errors'] += proj_img_stats['errors']
        
        # Optimize ServiceImage images
        self.stdout.write('Optimizing ServiceImage album images...')
        service_images = ServiceImage.objects.filter(image__isnull=False)
        serv_img_stats = self._optimize_model_images(
            service_images, 'image', 'ServiceImage', dry_run, force_optimize, batch_size
        )
        stats['service_images_optimized'] = serv_img_stats['projects_optimized']
        stats['space_saved'] += serv_img_stats['space_saved']
        stats['errors'] += serv_img_stats['errors']
        
        # Print final statistics
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('OPTIMIZATION COMPLETE'))
        self.stdout.write('='*50)
        self.stdout.write(f'Projects optimized: {stats["projects_optimized"]}')
        self.stdout.write(f'Services optimized: {stats["services_optimized"]}')
        self.stdout.write(f'Project album images optimized: {stats["project_images_optimized"]}')
        self.stdout.write(f'Service album images optimized: {stats["service_images_optimized"]}')
        self.stdout.write(f'Estimated space saved: {stats["space_saved"] / (1024*1024):.2f} MB')
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(f'Errors encountered: {stats["errors"]}')
            )
        
        if not dry_run:
            self.stdout.write('\nRecommendations for server deployment:')
            self.stdout.write('1. Run "python manage.py collectstatic" after deployment')
            self.stdout.write('2. Restart Gunicorn service')
            self.stdout.write('3. Clear any CDN/proxy caches')
            self.stdout.write('4. Consider running database VACUUM after deployment')

    def _optimize_model_images(self, queryset, field_name, model_name, dry_run, force_optimize, batch_size):
        """Optimize images for a specific model and field"""
        stats = {'projects_optimized': 0, 'space_saved': 0, 'errors': 0}
        total = queryset.count()
        
        if total == 0:
            self.stdout.write(f'  No {model_name} images found.')
            return stats
        
        self.stdout.write(f'  Found {total} {model_name} images to process...')
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = queryset[i:i + batch_size]
            
            for instance in batch:
                try:
                    image_field = getattr(instance, field_name)
                    
                    if not image_field:
                        continue
                    
                    # Get original file size
                    try:
                        original_size = image_field.size
                    except (OSError, FileNotFoundError):
                        self.stdout.write(
                            self.style.WARNING(f'    File not found for {model_name} ID {instance.id}')
                        )
                        stats['errors'] += 1
                        continue
                    
                    # Check if optimization is needed
                    if not force_optimize and not should_optimize_image(image_field):
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            f'    Would optimize {model_name} ID {instance.id} '
                            f'({original_size / (1024*1024):.2f} MB)'
                        )
                        stats['projects_optimized'] += 1
                        continue
                    
                    # Optimize the image
                    self.stdout.write(
                        f'    Optimizing {model_name} ID {instance.id}...'
                    )
                    
                    optimized = optimize_image(
                        image_field,
                        max_width=1920 if field_name != 'icon' else 512,
                        max_height=1080 if field_name != 'icon' else 512,
                        quality=85 if field_name != 'icon' else 90
                    )
                    
                    if optimized:
                        # Save the optimized image
                        with transaction.atomic():
                            setattr(instance, field_name, optimized)
                            instance.save()
                        
                        # Calculate space saved
                        try:
                            new_size = getattr(instance, field_name).size
                            space_saved = original_size - new_size
                            stats['space_saved'] += max(0, space_saved)
                        except (OSError, FileNotFoundError):
                            pass
                        
                        stats['projects_optimized'] += 1
                        self.stdout.write(
                            f'    ✓ Optimized {model_name} ID {instance.id}'
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'    Failed to optimize {model_name} ID {instance.id}')
                        )
                        stats['errors'] += 1
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    Error processing {model_name} ID {instance.id}: {e}')
                    )
                    stats['errors'] += 1
            
            # Add a small delay between batches to avoid overwhelming the system
            if not dry_run and batch_size > 1:
                time.sleep(0.1)
        
        return stats
