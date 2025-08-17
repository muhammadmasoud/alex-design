"""
Management command to re-optimize all images with high quality settings
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from portfolio.models import Project, ServiceItem, ProjectImage, ServiceImage
from portfolio.image_utils import optimize_image
from django.conf import settings


class Command(BaseCommand):
    help = 'Re-optimize all images with high quality settings for better visual quality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization even if images seem optimized',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if not getattr(settings, 'IMAGE_OPTIMIZATION', {}).get('ENABLE_OPTIMIZATION', False):
            self.stdout.write(
                self.style.WARNING('Image optimization is disabled in settings')
            )
            return

        self.stdout.write('Starting high-quality image re-optimization...\n')
        
        total_optimized = 0
        total_size_before = 0
        total_size_after = 0
        
        # Re-optimize project images
        self.stdout.write('Processing project images...')
        for project in Project.objects.all():
            if project.image:
                result = self.optimize_single_image(project, 'image', dry_run, force)
                if result:
                    total_optimized += 1
                    total_size_before += result['size_before']
                    total_size_after += result['size_after']
        
        # Re-optimize project album images
        self.stdout.write('Processing project album images...')
        for project_image in ProjectImage.objects.all():
            if project_image.image:
                result = self.optimize_single_image(project_image, 'image', dry_run, force)
                if result:
                    total_optimized += 1
                    total_size_before += result['size_before']
                    total_size_after += result['size_after']
        
        # Re-optimize service icons
        self.stdout.write('Processing service icons...')
        for service in ServiceItem.objects.all():
            if service.icon:
                result = self.optimize_single_image(service, 'icon', dry_run, force)
                if result:
                    total_optimized += 1
                    total_size_before += result['size_before']
                    total_size_after += result['size_after']
        
        # Re-optimize service album images
        self.stdout.write('Processing service album images...')
        for service_image in ServiceImage.objects.all():
            if service_image.image:
                result = self.optimize_single_image(service_image, 'image', dry_run, force)
                if result:
                    total_optimized += 1
                    total_size_before += result['size_before']
                    total_size_after += result['size_after']
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Re-optimization completed!')
        self.stdout.write(f'Images processed: {total_optimized}')
        
        if total_size_before > 0:
            reduction_percent = ((total_size_before - total_size_after) / total_size_before) * 100
            size_before_mb = total_size_before / (1024 * 1024)
            size_after_mb = total_size_after / (1024 * 1024)
            
            self.stdout.write(f'Total size before: {size_before_mb:.2f} MB')
            self.stdout.write(f'Total size after: {size_after_mb:.2f} MB')
            
            if reduction_percent > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Size reduction: {reduction_percent:.1f}%')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Size increase: {abs(reduction_percent):.1f}% (higher quality)')
                )

    def optimize_single_image(self, obj, field_name, dry_run=False, force=False):
        """Optimize a single image field"""
        image_field = getattr(obj, field_name)
        
        if not image_field:
            return None
        
        try:
            # Get original file size
            original_size = image_field.size if hasattr(image_field, 'size') else 0
            
            # Skip if image is already small and high quality (unless forced)
            if not force and original_size < 500 * 1024:  # Skip files smaller than 500KB
                return None
            
            model_name = obj.__class__.__name__
            obj_id = obj.id
            field_display = f"{model_name}({obj_id}).{field_name}"
            
            if dry_run:
                self.stdout.write(f'Would re-optimize: {field_display} ({original_size/1024:.1f}KB)')
                return {'size_before': original_size, 'size_after': original_size}
            
            # Create backup of original path
            original_path = image_field.name
            
            # Optimize with high quality settings
            optimized = optimize_image(
                image_field,
                max_width=2560,
                max_height=1440,
                quality=96  # Very high quality
            )
            
            if optimized:
                # Save the optimized image
                setattr(obj, field_name, optimized)
                obj.save(update_fields=[field_name])
                
                new_size = optimized.size
                size_change = ((new_size - original_size) / original_size) * 100
                
                self.stdout.write(
                    f'✓ Re-optimized: {field_display} '
                    f'({original_size/1024:.1f}KB → {new_size/1024:.1f}KB, '
                    f'{size_change:+.1f}%)'
                )
                
                return {'size_before': original_size, 'size_after': new_size}
            else:
                self.stdout.write(
                    self.style.WARNING(f'Failed to re-optimize: {field_display}')
                )
                return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error re-optimizing {field_display}: {e}')
            )
            return None
