from django.core.management.base import BaseCommand
from portfolio.models import Project, Service


class Command(BaseCommand):
    help = 'Populate database with sample projects and services with categories'

    def handle(self, *args, **options):
        # Clear existing data
        Project.objects.all().delete()
        Service.objects.all().delete()

        # Create sample projects
        projects_data = [
            {
                'title': 'Modern Villa',
                'description': 'A contemporary residential design featuring clean lines and open spaces.',
                'category': 'Residential',
                'subcategory': 'Exterior'
            },
            {
                'title': 'Luxury Kitchen Design',
                'description': 'High-end kitchen design with premium materials and smart appliances.',
                'category': 'Residential',
                'subcategory': 'Kitchen'
            },
            {
                'title': 'Master Bedroom Suite',
                'description': 'Elegant master bedroom with walk-in closet and en-suite bathroom.',
                'category': 'Residential',
                'subcategory': 'Bedroom'
            },
            {
                'title': 'Modern Living Room',
                'description': 'Open-concept living space with contemporary furnishings.',
                'category': 'Residential',
                'subcategory': 'Living Room'
            },
            {
                'title': 'Corporate Office Building',
                'description': 'Modern office complex with sustainable design principles.',
                'category': 'Commercial',
                'subcategory': 'Office'
            },
            {
                'title': 'Fine Dining Restaurant',
                'description': 'Upscale restaurant interior with warm ambiance and open kitchen.',
                'category': 'Commercial',
                'subcategory': 'Restaurant'
            },
            {
                'title': 'Retail Shopping Center',
                'description': 'Large retail space with modern storefront designs.',
                'category': 'Commercial',
                'subcategory': 'Retail'
            },
            {
                'title': 'Public Library',
                'description': 'Community library with contemporary architecture and reading spaces.',
                'category': 'Public',
                'subcategory': 'Educational'
            },
            {
                'title': 'Art Gallery',
                'description': 'Modern art gallery with flexible exhibition spaces.',
                'category': 'Public',
                'subcategory': 'Cultural'
            },
            {
                'title': 'Garden Landscape',
                'description': 'Beautiful landscape design for a private residence.',
                'category': 'Residential',
                'subcategory': 'Garden'
            },
        ]

        for project_data in projects_data:
            Project.objects.create(**project_data)

        # Create sample services
        services_data = [
            {
                'name': 'Architectural Design',
                'description': 'Complete architectural design services for residential and commercial projects.',
                'category': 'Design'
            },
            {
                'name': 'Urban Planning',
                'description': 'Strategic urban planning and development consulting.',
                'category': 'Planning'
            },
            {
                'name': 'Interior Design',
                'description': 'Professional interior design for all types of spaces.',
                'category': 'Design'
            },
            {
                'name': 'Construction Consulting',
                'description': 'Expert consultation throughout the construction process.',
                'category': 'Consulting'
            },
            {
                'name': '3D Visualization',
                'description': 'High-quality 3D renderings and virtual walkthroughs.',
                'category': 'Visualization'
            },
        ]

        for service_data in services_data:
            Service.objects.create(**service_data)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(projects_data)} projects and {len(services_data)} services'
            )
        )
