"""
Management command to optimize all existing images to WebP format
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Project, ProjectImage, Service, ServiceImage
from portfolio.consolidated_image_optimizer import ConsolidatedImageOptimizer
import os

class Command(BaseCommand):
    help = 'Optimize all existing images to WebP format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of already optimized images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Image Optimization Process')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  DRY RUN MODE - No changes will be made')
            )
        
        optimizer = ConsolidatedImageOptimizer()
        
        # Optimize project main images
        self.stdout.write('\n📸 Optimizing Project Main Images...')
        projects = Project.objects.filter(image__isnull=False)
        project_count = 0
        
        for project in projects:
            if project.image and project.image.name:
                original_path = project.image.name
                original_ext = os.path.splitext(original_path)[1].lower()
                
                # Skip if already WebP and not forcing
                if original_ext == '.webp' and not force:
                    self.stdout.write(f"   ⏭️  {original_path} (already WebP)")
                    continue
                
                if dry_run:
                    self.stdout.write(f"   🔄 Would optimize: {original_path}")
                else:
                    try:
                        result = optimizer.optimize_and_convert_image(project.image, project)
                        if result:
                            self.stdout.write(f"   ✅ Optimized: {original_path}")
                            project_count += 1
                        else:
                            self.stdout.write(f"   ❌ Failed: {original_path}")
                    except Exception as e:
                        self.stdout.write(f"   ❌ Error: {original_path} - {e}")
        
        # Optimize project album images
        self.stdout.write('\n🖼️  Optimizing Project Album Images...')
        project_images = ProjectImage.objects.all()
        album_count = 0
        
        for project_image in project_images:
            if project_image.image and project_image.image.name:
                original_path = project_image.image.name
                original_ext = os.path.splitext(original_path)[1].lower()
                
                # Skip if already WebP and not forcing
                if original_ext == '.webp' and not force:
                    self.stdout.write(f"   ⏭️  {original_path} (already WebP)")
                    continue
                
                if dry_run:
                    self.stdout.write(f"   🔄 Would optimize: {original_path}")
                else:
                    try:
                        result = optimizer.optimize_and_convert_image(project_image.image, project_image)
                        if result:
                            self.stdout.write(f"   ✅ Optimized: {original_path}")
                            album_count += 1
                        else:
                            self.stdout.write(f"   ❌ Failed: {original_path}")
                    except Exception as e:
                        self.stdout.write(f"   ❌ Error: {original_path} - {e}")
        
        # Optimize service icons
        self.stdout.write('\n🎯 Optimizing Service Icons...')
        services = Service.objects.filter(icon__isnull=False)
        service_count = 0
        
        for service in services:
            if service.icon and service.icon.name:
                original_path = service.icon.name
                original_ext = os.path.splitext(original_path)[1].lower()
                
                # Skip if already WebP and not forcing
                if original_ext == '.webp' and not force:
                    self.stdout.write(f"   ⏭️  {original_path} (already WebP)")
                    continue
                
                if dry_run:
                    self.stdout.write(f"   🔄 Would optimize: {original_path}")
                else:
                    try:
                        result = optimizer.optimize_and_convert_image(service.icon, service)
                        if result:
                            self.stdout.write(f"   ✅ Optimized: {original_path}")
                            service_count += 1
                        else:
                            self.stdout.write(f"   ❌ Failed: {original_path}")
                    except Exception as e:
                        self.stdout.write(f"   ❌ Error: {original_path} - {e}")
        
        # Optimize service album images
        self.stdout.write('\n🖼️  Optimizing Service Album Images...')
        service_images = ServiceImage.objects.all()
        service_album_count = 0
        
        for service_image in service_images:
            if service_image.image and service_image.image.name:
                original_path = service_image.image.name
                original_ext = os.path.splitext(original_path)[1].lower()
                
                # Skip if already WebP and not forcing
                if original_ext == '.webp' and not force:
                    self.stdout.write(f"   ⏭️  {original_path} (already WebP)")
                    continue
                
                if dry_run:
                    self.stdout.write(f"   🔄 Would optimize: {original_path}")
                else:
                    try:
                        result = optimizer.optimize_and_convert_image(service_image.image, service_image)
                        if result:
                            self.stdout.write(f"   ✅ Optimized: {original_path}")
                            service_album_count += 1
                        else:
                            self.stdout.write(f"   ❌ Failed: {original_path}")
                    except Exception as e:
                        self.stdout.write(f"   ❌ Error: {original_path} - {e}")
        
        # Summary
        total_optimized = project_count + album_count + service_count + service_album_count
        
        self.stdout.write('\n📊 Optimization Summary:')
        self.stdout.write(f"   Project main images: {project_count}")
        self.stdout.write(f"   Project album images: {album_count}")
        self.stdout.write(f"   Service icons: {service_count}")
        self.stdout.write(f"   Service album images: {service_album_count}")
        self.stdout.write(f"   Total optimized: {total_optimized}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN COMPLETED - No changes made')
            )
            self.stdout.write('💡 To actually optimize images, run without --dry-run')
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Image optimization completed successfully!')
            )
            
            # Check storage savings
            self.stdout.write('\n💾 Checking storage savings...')
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                total_files = sum([len(files) for r, d, files in os.walk(media_root)])
                self.stdout.write(f"   Total files in media: {total_files}")
                
                # Count WebP files
                webp_count = 0
                for root, dirs, files in os.walk(media_root):
                    for file in files:
                        if file.lower().endswith('.webp'):
                            webp_count += 1
                
                self.stdout.write(f"   WebP files: {webp_count}")
                self.stdout.write(f"   Conversion rate: {(webp_count/total_files*100):.1f}%" if total_files > 0 else "N/A")
