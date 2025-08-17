"""
Management command to check and fix broken image URLs
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Project, Service, ProjectImage, ServiceImage
import os


class Command(BaseCommand):
    help = 'Check and report broken image URLs in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix broken URLs by removing invalid entries',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        self.stdout.write('Checking for broken image URLs...\n')
        
        # Check Projects
        self.stdout.write('Checking Project images...')
        broken_projects = 0
        for project in Project.objects.filter(image__isnull=False):
            if project.image:
                image_path = os.path.join(settings.MEDIA_ROOT, project.image.name)
                if not os.path.exists(image_path):
                    self.stdout.write(
                        self.style.ERROR(f'Missing: Project "{project.title}" - {project.image.name}')
                    )
                    broken_projects += 1
                    
                    if fix_mode and not dry_run:
                        project.image = None
                        project.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'  Fixed: Removed broken image reference')
                        )
        
        # Check Services
        self.stdout.write('\nChecking Service icons...')
        broken_services = 0
        for service in Service.objects.filter(icon__isnull=False):
            if service.icon:
                icon_path = os.path.join(settings.MEDIA_ROOT, service.icon.name)
                if not os.path.exists(icon_path):
                    self.stdout.write(
                        self.style.ERROR(f'Missing: Service "{service.name}" - {service.icon.name}')
                    )
                    broken_services += 1
                    
                    if fix_mode and not dry_run:
                        service.icon = None
                        service.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'  Fixed: Removed broken icon reference')
                        )
        
        # Check Project Album Images
        self.stdout.write('\nChecking Project album images...')
        broken_project_images = 0
        for project_image in ProjectImage.objects.filter(image__isnull=False):
            if project_image.image:
                image_path = os.path.join(settings.MEDIA_ROOT, project_image.image.name)
                if not os.path.exists(image_path):
                    self.stdout.write(
                        self.style.ERROR(f'Missing: Project "{project_image.project.title}" album image - {project_image.image.name}')
                    )
                    broken_project_images += 1
                    
                    if fix_mode and not dry_run:
                        project_image.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'  Fixed: Deleted broken album image')
                        )
        
        # Check Service Album Images
        self.stdout.write('\nChecking Service album images...')
        broken_service_images = 0
        for service_image in ServiceImage.objects.filter(image__isnull=False):
            if service_image.image:
                image_path = os.path.join(settings.MEDIA_ROOT, service_image.image.name)
                if not os.path.exists(image_path):
                    self.stdout.write(
                        self.style.ERROR(f'Missing: Service "{service_image.service.name}" album image - {service_image.image.name}')
                    )
                    broken_service_images += 1
                    
                    if fix_mode and not dry_run:
                        service_image.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'  Fixed: Deleted broken album image')
                        )
        
        # Summary
        total_broken = broken_projects + broken_services + broken_project_images + broken_service_images
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('BROKEN IMAGE REPORT')
        self.stdout.write('='*50)
        self.stdout.write(f'Project images: {broken_projects} broken')
        self.stdout.write(f'Service icons: {broken_services} broken')
        self.stdout.write(f'Project album images: {broken_project_images} broken')
        self.stdout.write(f'Service album images: {broken_service_images} broken')
        self.stdout.write(f'Total broken: {total_broken}')
        
        if total_broken == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ All image URLs are valid!'))
        else:
            if fix_mode and not dry_run:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Fixed {total_broken} broken image references'))
            else:
                self.stdout.write(self.style.WARNING(f'\n⚠ Found {total_broken} broken image references'))
                self.stdout.write('Run with --fix to automatically remove broken references')
                self.stdout.write('Run with --dry-run --fix to see what would be fixed')
