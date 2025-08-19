from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Project, Service

User = get_user_model()

class OrderResequencingTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a superuser for authenticated requests
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        
        # Create test projects with sequential orders
        self.projects = []
        for i in range(1, 6):  # Create 5 projects with orders 1-5
            project = Project.objects.create(
                title=f'Project {i}',
                description=f'Description {i}',
                project_date='2025-08-19',  # Required field
                order=i
            )
            self.projects.append(project)
    
    def test_project_deletion_resequencing(self):
        """Test that deleting a project automatically resequences remaining projects"""
        # Initial state: projects with orders 1, 2, 3, 4, 5
        initial_orders = [p.order for p in Project.objects.order_by('order')]
        self.assertEqual(initial_orders, [1, 2, 3, 4, 5])
        
        # Delete project with order 3 (middle project)
        middle_project = self.projects[2]  # Project 3
        response = self.client.delete(f'/api/projects/{middle_project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that remaining projects are resequenced
        remaining_orders = [p.order for p in Project.objects.order_by('order')]
        self.assertEqual(remaining_orders, [1, 2, 3, 4])  # Orders should be 1, 2, 3, 4 (no gaps)
        
        # Verify specific projects are in correct positions
        projects_by_title = {p.title: p.order for p in Project.objects.all()}
        self.assertEqual(projects_by_title['Project 1'], 1)
        self.assertEqual(projects_by_title['Project 2'], 2)
        self.assertEqual(projects_by_title['Project 4'], 3)  # Should move from 4 to 3
        self.assertEqual(projects_by_title['Project 5'], 4)  # Should move from 5 to 4
    
    def test_service_deletion_resequencing(self):
        """Test that deleting a service automatically resequences remaining services"""
        # Create test services
        services = []
        for i in range(1, 6):  # Create 5 services with orders 1-5
            service = Service.objects.create(
                name=f'Service {i}',
                description=f'Description {i}',
                price=100.00 * i,
                order=i
            )
            services.append(service)
        
        # Initial state: services with orders 1, 2, 3, 4, 5
        initial_orders = [s.order for s in Service.objects.order_by('order')]
        self.assertEqual(initial_orders, [1, 2, 3, 4, 5])
        
        # Delete service with order 2 (early service)
        early_service = services[1]  # Service 2
        response = self.client.delete(f'/api/services/{early_service.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that remaining services are resequenced
        remaining_orders = [s.order for s in Service.objects.order_by('order')]
        self.assertEqual(remaining_orders, [1, 2, 3, 4])  # Orders should be 1, 2, 3, 4 (no gaps)
        
        # Verify specific services are in correct positions
        services_by_name = {s.name: s.order for s in Service.objects.all()}
        self.assertEqual(services_by_name['Service 1'], 1)
        self.assertEqual(services_by_name['Service 3'], 2)  # Should move from 3 to 2
        self.assertEqual(services_by_name['Service 4'], 3)  # Should move from 4 to 3
        self.assertEqual(services_by_name['Service 5'], 4)  # Should move from 5 to 4
    
    def test_delete_last_item_no_resequencing_needed(self):
        """Test that deleting the last item doesn't affect other orders"""
        # Delete the last project (order 5)
        last_project = self.projects[4]  # Project 5
        response = self.client.delete(f'/api/projects/{last_project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that remaining projects keep their original orders
        remaining_orders = [p.order for p in Project.objects.order_by('order')]
        self.assertEqual(remaining_orders, [1, 2, 3, 4])  # No gaps, no changes needed
    
    def test_delete_first_item_resequencing(self):
        """Test that deleting the first item resequences all others"""
        # Delete the first project (order 1)
        first_project = self.projects[0]  # Project 1
        response = self.client.delete(f'/api/projects/{first_project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that remaining projects are resequenced
        remaining_orders = [p.order for p in Project.objects.order_by('order')]
        self.assertEqual(remaining_orders, [1, 2, 3, 4])  # All should shift down by 1
        
        # Verify specific projects moved correctly
        projects_by_title = {p.title: p.order for p in Project.objects.all()}
        self.assertEqual(projects_by_title['Project 2'], 1)  # Should move from 2 to 1
        self.assertEqual(projects_by_title['Project 3'], 2)  # Should move from 3 to 2
        self.assertEqual(projects_by_title['Project 4'], 3)  # Should move from 4 to 3
        self.assertEqual(projects_by_title['Project 5'], 4)  # Should move from 5 to 4
