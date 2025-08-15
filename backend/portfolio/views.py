from django.shortcuts import render
from rest_framework import viewsets
from .models import Project, Service
from .serializers import ProjectSerializer, ServiceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .auth_serializers import RegistrationSerializer, LoginSerializer
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import FilterSet, CharFilter
import django_filters
from django.db import models
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action, permission_classes
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
from .contact_serializers import ContactSerializer

# Create your views here.

class ProjectFilter(FilterSet):
    category = CharFilter(method='filter_category')
    subcategory = CharFilter(method='filter_subcategory')
    search = CharFilter(method='filter_search')
    
    def filter_category(self, queryset, name, value):
        # Filter by category name
        return queryset.filter(category__name__iexact=value)
    
    def filter_subcategory(self, queryset, name, value):
        # Filter by subcategory name
        return queryset.filter(subcategory__name__iexact=value)
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) | 
            models.Q(description__icontains=value)
        )
    
    class Meta:
        model = Project
        fields = ['category', 'subcategory']


class ServiceFilter(FilterSet):
    category = CharFilter(method='filter_category')
    subcategory = CharFilter(method='filter_subcategory')
    search = CharFilter(method='filter_search')
    
    def filter_category(self, queryset, name, value):
        # Filter by category name
        return queryset.filter(category__name__iexact=value)
    
    def filter_subcategory(self, queryset, name, value):
        # Filter by subcategory name
        return queryset.filter(subcategory__name__iexact=value)
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) | 
            models.Q(description__icontains=value)
        )
    
    class Meta:
        model = Service
        fields = ['category', 'subcategory']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif isinstance(request.data, dict):
            return super().create(request, *args, **kwargs)
        else:
            raise ValidationError("Invalid data format. Expected a dictionary or a list of dictionaries.")


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategorySubcategoriesView(APIView):
    """
    API endpoint to get categories and subcategories for projects and services.
    """
    def get(self, request):
        model_type = request.GET.get('type', 'project')  # 'project' or 'service'
        category = request.GET.get('category')
        
        # Import models here to avoid circular imports
        from .models import ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory
        
        if model_type == 'service':
            # Get service categories from database
            if category:
                # Find the category and return its subcategories
                try:
                    cat_obj = ServiceCategory.objects.get(name=category)
                    subcategories = [
                        {'value': sub.name, 'label': sub.name} 
                        for sub in cat_obj.subcategories.all()
                    ]
                    return Response({
                        'category': category,
                        'subcategories': subcategories
                    })
                except ServiceCategory.DoesNotExist:
                    return Response({
                        'category': category,
                        'subcategories': []
                    })
            else:
                # Return all service categories and their subcategories
                categories = ServiceCategory.objects.prefetch_related('subcategories').all()
                formatted_categories = {}
                category_list = []
                
                for cat in categories:
                    subcategories = [
                        {'value': sub.name, 'label': sub.name} 
                        for sub in cat.subcategories.all()
                    ]
                    formatted_categories[cat.name] = subcategories
                    category_list.append({'value': cat.name, 'label': cat.name})
                
                return Response({
                    'type': model_type,
                    'categories': formatted_categories,
                    'category_list': category_list
                })
        else:
            # Get project categories from database
            if category:
                # Find the category and return its subcategories
                try:
                    cat_obj = ProjectCategory.objects.get(name=category)
                    subcategories = [
                        {'value': sub.name, 'label': sub.name} 
                        for sub in cat_obj.subcategories.all()
                    ]
                    return Response({
                        'category': category,
                        'subcategories': subcategories
                    })
                except ProjectCategory.DoesNotExist:
                    return Response({
                        'category': category,
                        'subcategories': []
                    })
            else:
                # Return all project categories and their subcategories
                categories = ProjectCategory.objects.prefetch_related('subcategories').all()
                formatted_categories = {}
                category_list = []
                
                for cat in categories:
                    subcategories = [
                        {'value': sub.name, 'label': sub.name} 
                        for sub in cat.subcategories.all()
                    ]
                    formatted_categories[cat.name] = subcategories
                    category_list.append({'value': cat.name, 'label': cat.name})
                
                return Response({
                    'type': model_type,
                    'categories': formatted_categories,
                    'category_list': category_list
                })


class AdminDashboardView(APIView):
    """
    Admin dashboard API endpoint for superuser only
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        user = request.user
        
        # Import models here to avoid circular imports
        from .models import ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory
        
        # Get statistics
        projects_count = Project.objects.count()
        services_count = Service.objects.count()
        recent_projects = Project.objects.order_by('-created_at')[:5]
        
        # Get dynamic categories
        project_categories = ProjectCategory.objects.prefetch_related('subcategories').all()
        service_categories = ServiceCategory.objects.prefetch_related('subcategories').all()
        
        # Format project categories
        project_cats_formatted = {}
        for cat in project_categories:
            subcategories = [
                {'id': sub.id, 'name': sub.name, 'description': sub.description} 
                for sub in cat.subcategories.all()
            ]
            project_cats_formatted[cat.name] = subcategories
        
        # Format service categories
        service_cats_formatted = {}
        for cat in service_categories:
            subcategories = [
                {'id': sub.id, 'name': sub.name, 'description': sub.description} 
                for sub in cat.subcategories.all()
            ]
            service_cats_formatted[cat.name] = subcategories
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            },
            'statistics': {
                'projects_count': projects_count,
                'services_count': services_count,
            },
            'recent_projects': ProjectSerializer(recent_projects, many=True).data,
            'categories': {
                'projects': project_cats_formatted,
                'services': service_cats_formatted
            }
        })


class AdminCheckView(APIView):
    """
    Check if current user is admin
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'is_admin': user.is_superuser or user.is_staff,
            'is_superuser': user.is_superuser,
            'username': user.username,
            'email': user.email
        })


class ContactView(APIView):
    """
    Handle contact form submissions - no authentication required
    """
    permission_classes = []  # No authentication required
    
    def post(self, request):
        """Handle contact form submission"""
        print(f"Contact form data received: {request.data}")
        
        serializer = ContactSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Send the email
                success = serializer.save()
                
                if success:
                    return Response({
                        'message': 'Thank you for your message! We will get back to you soon.',
                        'success': True
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'message': 'Message received but email notification failed. We will still respond to you.',
                        'success': True
                    }, status=status.HTTP_200_OK)
                    
            except Exception as e:
                print(f"Contact form error: {str(e)}")
                return Response({
                    'message': 'Message received but email notification failed. We will still respond to you.',
                    'success': True
                }, status=status.HTTP_200_OK)
        
        print(f"Validation errors: {serializer.errors}")
        return Response({
            'errors': serializer.errors,
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
