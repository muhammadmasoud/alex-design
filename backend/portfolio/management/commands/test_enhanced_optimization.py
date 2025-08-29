"""
Management command to test the enhanced image optimization system
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Project, ProjectImage
from portfolio.enhanced_image_optimizer import EnhancedImageOptimizer
import os

class Command(BaseCommand):
    help = 'Test the enhanced image optimization system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Testing Enhanced Image Optimization System')
        )
        
        # Check settings
        self.stdout.write('\n📋 Current Settings:')
        image_settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
        for key, value in image_settings.items():
            self.stdout.write(f"   {key}: {value}")
        
        # Check existing images
        self.stdout.write('\n📊 Current Image Status:')
        projects_with_images = Project.objects.filter(image__isnull=False).count()
        project_images = ProjectImage.objects.count()
        
        self.stdout.write(f"   Projects with main images: {projects_with_images}")
        self.stdout.write(f"   Project album images: {project_images}")
        
        # Test optimizer
        self.stdout.write('\n🧪 Testing Optimizer:')
        optimizer = EnhancedImageOptimizer()
        
        self.stdout.write(f"   WebP Quality: {optimizer.webp_quality}")
        self.stdout.write(f"   Delete Original: {optimizer.delete_original}")
        self.stdout.write(f"   Compression Method: {optimizer.compression_method}")
        self.stdout.write(f"   Thumbnail Sizes: {len(optimizer.thumbnail_sizes)}")
        
        # Show thumbnail sizes
        for size_name, dimensions in optimizer.thumbnail_sizes.items():
            self.stdout.write(f"     {size_name}: {dimensions}")
        
        # Check media directory
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            total_files = sum([len(files) for r, d, files in os.walk(media_root)])
            self.stdout.write(f"\n💾 Media Directory: {media_root}")
            self.stdout.write(f"   Total files: {total_files}")
            
            # Count by extension
            extensions = {}
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            self.stdout.write('\n📁 Files by Extension:')
            for ext, count in sorted(extensions.items()):
                self.stdout.write(f"   {ext}: {count}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN - No changes made')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Test completed successfully')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n💡 To optimize existing images, run:')
        )
        self.stdout.write('   python manage.py optimize_existing_images')
