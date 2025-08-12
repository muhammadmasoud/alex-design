from django.core.management.base import BaseCommand
from portfolio.models import Project, Service
from portfolio.constants import PROJECT_CATEGORIES, SERVICE_CATEGORIES
import random

class Command(BaseCommand):
    help = 'Create sample projects and services with categories and subcategories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=5,
            help='Number of sample projects to create'
        )
        parser.add_argument(
            '--services',
            type=int,
            default=3,
            help='Number of sample services to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create sample projects
        project_count = 0
        for i in range(options['projects']):
            # Pick random category and subcategory
            category = random.choice(list(PROJECT_CATEGORIES.keys()))
            subcategories = PROJECT_CATEGORIES[category]
            subcategory = random.choice(subcategories)[0] if subcategories else None

            project = Project.objects.create(
                title=f"Sample {category} Project {i+1}",
                description=f"This is a sample {category.lower()} project showcasing {subcategory.lower() if subcategory else 'various aspects'} of architectural design.",
                category=category,
                subcategory=subcategory
            )
            project_count += 1
            self.stdout.write(f"Created project: {project.title} ({category} - {subcategory})")

        # Create sample services
        service_count = 0
        for i in range(options['services']):
            # Pick random category and subcategory
            category = random.choice(list(SERVICE_CATEGORIES.keys()))
            subcategories = SERVICE_CATEGORIES[category]
            subcategory = random.choice(subcategories)[0] if subcategories else None

            service = Service.objects.create(
                name=f"Sample {subcategory or category} Service {i+1}",
                description=f"Professional {subcategory.lower() if subcategory else category.lower()} services for your architectural needs.",
                category=category,
                subcategory=subcategory
            )
            service_count += 1
            self.stdout.write(f"Created service: {service.name} ({category} - {subcategory})")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {project_count} projects and {service_count} services!'
            )
        )
        self.stdout.write('You can view them in the Django admin or through the API endpoints.')
