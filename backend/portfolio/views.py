from django.shortcuts import render
from rest_framework import viewsets
from .models import Project, Service, ProjectImage, ServiceImage
from .serializers import ProjectSerializer, ServiceSerializer, ProjectImageSerializer, ServiceImageSerializer
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
import shutil
from .contact_serializers import ContactSerializer
from django.db import transaction
from django.middleware.csrf import get_token
from django.conf import settings
from django.db import models


# Create your views here.

class ProjectFilter(FilterSet):
    category = CharFilter(method='filter_category')
    subcategory = CharFilter(method='filter_subcategory')
    search = CharFilter(method='filter_search')
    
    def filter_category(self, queryset, name, value):
        # Filter by category name (updated for many-to-many relationship)
        return queryset.filter(categories__name__iexact=value)
    
    def filter_subcategory(self, queryset, name, value):
        # Filter by subcategory name (updated for many-to-many relationship)
        return queryset.filter(subcategories__name__iexact=value)
    
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
        # Filter by category name (updated for many-to-many relationship)
        return queryset.filter(categories__name__iexact=value)
    
    def filter_subcategory(self, queryset, name, value):
        # Filter by subcategory name (updated for many-to-many relationship)
        return queryset.filter(subcategories__name__iexact=value)
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) | 
            models.Q(description__icontains=value)
        )
    
    class Meta:
        model = Service
        fields = ['category', 'subcategory']


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['project_date', 'title', 'order']
    ordering = ['order', '-project_date']

    def get_queryset(self):
        """Optimized queryset with prefetching to avoid N+1 queries"""
        return Project.objects.select_related().prefetch_related(
            'categories',
            'subcategories', 
            'album_images'
        ).annotate(
            album_images_count_annotated=models.Count('album_images')
        ).order_by('order', '-project_date')

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Capture original filename from uploaded image
        image_file = self.request.FILES.get('image')
        
        # Get the order from the data
        order = serializer.validated_data.get('order')
        
        with transaction.atomic():
            # If an order is specified, shift existing projects to make room
            if order is not None and order >= 1:
                # Shift all projects with order >= new_order by +1
                Project.objects.filter(order__gte=order).update(
                    order=models.F('order') + 1
                )
            
            # Save the project with the image filename if provided
            if image_file:
                serializer.save(original_filename=image_file.name)
            else:
                serializer.save()

    def perform_update(self, serializer):
        # Capture original filename from uploaded image if a new one is provided
        image_file = self.request.FILES.get('image')
        if image_file:
            serializer.save(original_filename=image_file.name)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to automatically resequence order values
        when a project is deleted
        """
        deleted_order = instance.order
        
        with transaction.atomic():
            # Delete the project first
            instance.delete()
            
            # Resequence all projects with order higher than the deleted one
            Project.objects.filter(order__gt=deleted_order).update(
                order=models.F('order') - 1
            )

    def create(self, request, *args, **kwargs):
        try:
            print("=== PROJECT CREATION ATTEMPT ===")
            print(f"Data received: {request.data}")
            print(f"Files received: {request.FILES}")
            
            if isinstance(request.data, list):
                serializer = self.get_serializer(data=request.data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif isinstance(request.data, dict):
                return super().create(request, *args, **kwargs)
            else:
                raise ValidationError("Invalid data format. Expected a dictionary or a list of dictionaries.")
        except Exception as e:
            print(f"❌ Error in project creation: {e}")
            import traceback
            traceback.print_exc()
            raise

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reorder(self, request, pk=None):
        """
        Reorder projects. Accepts 'direction' (up/down) or 'new_order' parameter.
        """
        project = self.get_object()
        direction = request.data.get('direction')
        new_order = request.data.get('new_order')
        
        if new_order is not None:
            # Direct order assignment
            try:
                new_order = int(new_order)
                if new_order < 1:
                    return Response({'error': 'Order must be >= 1'}, status=status.HTTP_400_BAD_REQUEST)
                
                with transaction.atomic():
                    old_order = project.order
                    
                    if new_order > old_order:
                        # Moving down: shift items up
                        Project.objects.filter(
                            order__gt=old_order,
                            order__lte=new_order
                        ).update(order=models.F('order') - 1)
                    elif new_order < old_order:
                        # Moving up: shift items down
                        Project.objects.filter(
                            order__gte=new_order,
                            order__lt=old_order
                        ).update(order=models.F('order') + 1)
                    
                    project.order = new_order
                    project.save()
                
                return Response({'message': 'Project reordered successfully'})
            except ValueError:
                return Response({'error': 'Invalid order value'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif direction in ['up', 'down']:
            # Up/down arrow functionality
            with transaction.atomic():
                if direction == 'up':
                    # Find the project with the order just before this one
                    previous_project = Project.objects.filter(
                        order__lt=project.order
                    ).order_by('-order').first()
                    
                    if previous_project:
                        # Swap orders
                        project.order, previous_project.order = previous_project.order, project.order
                        project.save()
                        previous_project.save()
                        return Response({'message': 'Project moved up successfully'})
                    else:
                        return Response({'error': 'Project is already first'}, status=status.HTTP_400_BAD_REQUEST)
                
                else:  # direction == 'down'
                    # Find the project with the order just after this one
                    next_project = Project.objects.filter(
                        order__gt=project.order
                    ).order_by('order').first()
                    
                    if next_project:
                        # Swap orders
                        project.order, next_project.order = next_project.order, project.order
                        project.save()
                        next_project.save()
                        return Response({'message': 'Project moved down successfully'})
                    else:
                        return Response({'error': 'Project is already last'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({'error': 'Invalid direction or new_order parameter'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_reorder(self, request):
        """
        Bulk reorder projects based on array of IDs in desired order.
        """
        project_ids = request.data.get('project_ids', [])
        
        if not project_ids:
            return Response({'error': 'project_ids array is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                for index, project_id in enumerate(project_ids, start=1):
                    Project.objects.filter(id=project_id).update(order=index)
            
            return Response({'message': f'{len(project_ids)} projects reordered successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def debug_create(self, request):
        """
        Debug endpoint to see what data is being sent
        """
        print("=== DEBUG PROJECT CREATION ===")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"Data: {request.data}")
        print(f"Files: {request.FILES}")
        print(f"Query params: {request.query_params}")
        print("==============================")
        
        # Try to create the project and see what happens
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                print("✅ Serializer is valid")
                print(f"Validated data: {serializer.validated_data}")
                return Response({
                    'message': 'Data is valid',
                    'validated_data': serializer.validated_data
                })
            else:
                print("❌ Serializer validation failed")
                print(f"Errors: {serializer.errors}")
                return Response({
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'message': 'Exception occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order']
    ordering = ['order', 'name']

    def get_queryset(self):
        """Optimized queryset with prefetching to avoid N+1 queries"""
        return Service.objects.select_related().prefetch_related(
            'categories',
            'subcategories',
            'album_images'
        ).annotate(
            album_images_count_annotated=models.Count('album_images')
        ).order_by('order', 'name')

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Capture original filename from uploaded icon
        icon_file = self.request.FILES.get('icon')
        
        # Get the order from the data
        order = serializer.validated_data.get('order')
        
        with transaction.atomic():
            # If an order is specified, shift existing services to make room
            if order is not None and order >= 1:
                # Shift all services with order >= new_order by +1
                Service.objects.filter(order__gte=order).update(
                    order=models.F('order') + 1
                )
            
            # Save the service with the icon filename if provided
            if icon_file:
                serializer.save(original_filename=icon_file.name)
            else:
                serializer.save()

    def perform_update(self, serializer):
        # Capture original filename from uploaded icon if a new one is provided
        icon_file = self.request.FILES.get('icon')
        if icon_file:
            serializer.save(original_filename=icon_file.name)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to automatically resequence order values
        when a service is deleted
        """
        deleted_order = instance.order
        
        with transaction.atomic():
            # Delete the service first
            instance.delete()
            
            # Resequence all services with order higher than the deleted one
            Service.objects.filter(order__gt=deleted_order).update(
                order=models.F('order') - 1
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reorder(self, request, pk=None):
        """
        Reorder services. Accepts 'direction' (up/down) or 'new_order' parameter.
        """
        service = self.get_object()
        direction = request.data.get('direction')
        new_order = request.data.get('new_order')
        
        if new_order is not None:
            # Direct order assignment
            try:
                new_order = int(new_order)
                if new_order < 1:
                    return Response({'error': 'Order must be >= 1'}, status=status.HTTP_400_BAD_REQUEST)
                
                with transaction.atomic():
                    old_order = service.order
                    
                    if new_order > old_order:
                        # Moving down: shift items up
                        Service.objects.filter(
                            order__gt=old_order,
                            order__lte=new_order
                        ).update(order=models.F('order') - 1)
                    elif new_order < old_order:
                        # Moving up: shift items down
                        Service.objects.filter(
                            order__gte=new_order,
                            order__lt=old_order
                        ).update(order=models.F('order') + 1)
                    
                    service.order = new_order
                    service.save()
                
                return Response({'message': 'Service reordered successfully'})
            except ValueError:
                return Response({'error': 'Invalid order value'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif direction in ['up', 'down']:
            # Up/down arrow functionality
            with transaction.atomic():
                if direction == 'up':
                    # Find the service with the order just before this one
                    previous_service = Service.objects.filter(
                        order__lt=service.order
                    ).order_by('-order').first()
                    
                    if previous_service:
                        # Swap orders
                        service.order, previous_service.order = previous_service.order, service.order
                        service.save()
                        previous_service.save()
                        return Response({'message': 'Service moved up successfully'})
                    else:
                        return Response({'error': 'Service is already first'}, status=status.HTTP_400_BAD_REQUEST)
                
                else:  # direction == 'down'
                    # Find the service with the order just after this one
                    next_service = Service.objects.filter(
                        order__gt=service.order
                    ).order_by('order').first()
                    
                    if next_service:
                        # Swap orders
                        service.order, next_service.order = next_service.order, service.order
                        service.save()
                        next_service.save()
                        return Response({'message': 'Service moved down successfully'})
                    else:
                        return Response({'error': 'Service is already last'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({'error': 'Invalid direction or new_order parameter'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_reorder(self, request):
        """
        Bulk reorder services based on array of IDs in desired order.
        """
        service_ids = request.data.get('service_ids', [])
        
        if not service_ids:
            return Response({'error': 'service_ids array is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                for index, service_id in enumerate(service_ids, start=1):
                    Service.objects.filter(id=service_id).update(order=index)
            
            return Response({'message': f'{len(service_ids)} services reordered successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            # Get service categories from database with optimized queries
            if category:
                # Find the category and return its subcategories
                try:
                    cat_obj = ServiceCategory.objects.prefetch_related('subcategories').get(name=category)
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
                # Return all service categories and their subcategories with optimized query
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
            # Get project categories from database with optimized queries
            if category:
                # Find the category and return its subcategories
                try:
                    cat_obj = ProjectCategory.objects.prefetch_related('subcategories').get(name=category)
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
                # Return all project categories and their subcategories with optimized query
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


def calculate_storage_info():
    """Calculate storage usage information"""
    media_root = settings.MEDIA_ROOT
    total_size = 0
    file_count = 0
    
    # Calculate size of media files
    if os.path.exists(media_root):
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except OSError:
                    pass
    
    # Also check old projects directory if it exists
    old_projects_dir = os.path.join(os.path.dirname(media_root), 'projects')
    if os.path.exists(old_projects_dir):
        for root, dirs, files in os.walk(old_projects_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except OSError:
                    pass
    
    # Convert to MB
    total_size_mb = total_size / (1024 * 1024)
    
    # Get disk usage (free space)
    try:
        disk_usage = shutil.disk_usage(media_root)
        total_disk_gb = disk_usage.total / (1024 * 1024 * 1024)
        free_disk_gb = disk_usage.free / (1024 * 1024 * 1024)
        used_disk_gb = (disk_usage.total - disk_usage.free) / (1024 * 1024 * 1024)
    except OSError:
        total_disk_gb = free_disk_gb = used_disk_gb = 0
    
    return {
        'media_size_mb': round(total_size_mb, 2),
        'media_file_count': file_count,
        'disk_total_gb': round(total_disk_gb, 2),
        'disk_free_gb': round(free_disk_gb, 2),
        'disk_used_gb': round(used_disk_gb, 2),
        'disk_usage_percent': round((used_disk_gb / total_disk_gb * 100), 1) if total_disk_gb > 0 else 0
    }


class AdminStorageStatsView(APIView):
    """
    API endpoint for getting only storage statistics (faster than full dashboard)
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        storage_info = calculate_storage_info()
        return Response({
            'storage': storage_info
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
        recent_projects = Project.objects.order_by('order', '-project_date')[:5]
        
        # Get storage information
        storage_info = calculate_storage_info()
        
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
                'storage': storage_info,
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


class CSRFTokenView(APIView):
    """
    Return CSRF token for frontend use
    """
    permission_classes = []
    
    def get(self, request):
        token = get_token(request)
        return JsonResponse({'csrfToken': token})


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


class ProjectImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing project album images
    """
    serializer_class = ProjectImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order', 'created_at']

    def get_queryset(self):
        """Filter images by project if project_id is provided"""
        queryset = ProjectImage.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_upload(self, request):
        """
        Bulk upload multiple images for a project
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        with transaction.atomic():
            for i, image in enumerate(images):
                project_image = ProjectImage.objects.create(
                    project=project,
                    image=image,
                    original_filename=image.name,
                    order=i
                )
                created_images.append(project_image)
        
        serializer = self.get_serializer(created_images, many=True)
        return Response({
            'message': f'{len(created_images)} images uploaded successfully',
            'images': serializer.data
        }, status=status.HTTP_201_CREATED)


class ServiceImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service album images
    """
    serializer_class = ServiceImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order', 'created_at']

    def get_queryset(self):
        """Filter images by service if service_id is provided"""
        queryset = ServiceImage.objects.all()
        service_id = self.request.query_params.get('service_id', None)
        if service_id is not None:
            queryset = queryset.filter(service_id=service_id)
        return queryset

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Allow public read access, but require admin for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_upload(self, request):
        """
        Bulk upload multiple images for a service
        """
        service_id = request.data.get('service_id')
        if not service_id:
            return Response({'error': 'service_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        with transaction.atomic():
            for i, image in enumerate(images):
                service_image = ServiceImage.objects.create(
                    service=service,
                    image=image,
                    original_filename=image.name,
                    order=i
                )
                created_images.append(service_image)
        
        serializer = self.get_serializer(created_images, many=True)
        return Response({
            'message': f'{len(created_images)} images uploaded successfully',
            'images': serializer.data
        }, status=status.HTTP_201_CREATED)


class ProjectAlbumView(APIView):
    """
    API endpoint to get all album images for a specific project
    """
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            album_images = project.album_images.all()
            serializer = ProjectImageSerializer(album_images, many=True, context={'request': request})
            
            return Response({
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'image': request.build_absolute_uri(project.image.url) if project.image else None,
                    'category_name': project.get_category_name(),
                    'subcategory_name': project.get_subcategory_name()
                },
                'album_images': serializer.data,
                'total_images': len(serializer.data)
            })
        except Project.DoesNotExist:
            return Response({
                'error': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ServiceAlbumView(APIView):
    """
    API endpoint to get all album images for a specific service
    """
    def get(self, request, service_id):
        try:
            service = Service.objects.get(id=service_id)
            album_images = service.album_images.all()
            serializer = ServiceImageSerializer(album_images, many=True, context={'request': request})
            
            return Response({
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'description': service.description,
                    'icon': request.build_absolute_uri(service.icon.url) if service.icon else None,
                    'price': str(service.price),
                    'category_name': service.get_category_name(),
                    'subcategory_name': service.get_subcategory_name()
                },
                'album_images': serializer.data,
                'total_images': len(serializer.data)
            })
        except Service.DoesNotExist:
            return Response({
                'error': 'Service not found'
            }, status=status.HTTP_404_NOT_FOUND)


# Admin-specific ViewSets without pagination for dashboard
class AdminProjectViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for projects without pagination.
    Used by the admin dashboard to display all projects.
    """
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['project_date', 'title', 'order']
    ordering = ['order', '-project_date']
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """Optimized queryset with prefetching to avoid N+1 queries"""
        return Project.objects.select_related().prefetch_related(
            'categories',
            'subcategories', 
            'album_images'
        ).annotate(
            album_images_count_annotated=models.Count('album_images')
        ).order_by('order', '-project_date')

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # Capture original filename from uploaded image
        image_file = self.request.FILES.get('image')
        
        # Get the order from the data
        order = serializer.validated_data.get('order')
        
        with transaction.atomic():
            # If an order is specified, shift existing projects to make room
            if order is not None and order >= 1:
                # Shift all projects with order >= new_order by +1
                Project.objects.filter(order__gte=order).update(
                    order=models.F('order') + 1
                )
            
            # Save the project with the image filename if provided
            if image_file:
                serializer.save(original_filename=image_file.name)
            else:
                serializer.save()

    def perform_update(self, serializer):
        # Capture original filename from uploaded image if a new one is provided
        image_file = self.request.FILES.get('image')
        if image_file:
            serializer.save(original_filename=image_file.name)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to automatically resequence order values
        when a project is deleted
        """
        deleted_order = instance.order
        
        with transaction.atomic():
            # Delete the project first
            instance.delete()
            
            # Resequence all projects with order higher than the deleted one
            Project.objects.filter(order__gt=deleted_order).update(
                order=models.F('order') - 1
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reorder(self, request, pk=None):
        """
        Reorder projects. Accepts 'direction' (up/down) or 'new_order' parameter.
        """
        project = self.get_object()
        direction = request.data.get('direction')
        new_order = request.data.get('new_order')
        
        if new_order is not None:
            # Direct order assignment
            try:
                new_order = int(new_order)
                if new_order < 1:
                    return Response({'error': 'Order must be >= 1'}, status=status.HTTP_400_BAD_REQUEST)
                
                with transaction.atomic():
                    old_order = project.order
                    
                    if new_order > old_order:
                        # Moving down: shift items up
                        Project.objects.filter(
                            order__gt=old_order,
                            order__lte=new_order
                        ).update(order=models.F('order') - 1)
                    elif new_order < old_order:
                        # Moving up: shift items down
                        Project.objects.filter(
                            order__gte=new_order,
                            order__lt=old_order
                        ).update(order=models.F('order') + 1)
                    
                    project.order = new_order
                    project.save()
                
                return Response({'message': 'Project reordered successfully'})
            except ValueError:
                return Response({'error': 'Invalid order value'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif direction in ['up', 'down']:
            # Up/down arrow functionality
            with transaction.atomic():
                if direction == 'up':
                    # Find the project with the order just before this one
                    previous_project = Project.objects.filter(
                        order__lt=project.order
                    ).order_by('-order').first()
                    
                    if previous_project:
                        # Swap orders
                        project.order, previous_project.order = previous_project.order, project.order
                        project.save()
                        previous_project.save()
                        return Response({'message': 'Project moved up successfully'})
                    else:
                        return Response({'error': 'Project is already first'}, status=status.HTTP_400_BAD_REQUEST)
                
                else:  # direction == 'down'
                    # Find the project with the order just after this one
                    next_project = Project.objects.filter(
                        order__gt=project.order
                    ).order_by('order').first()
                    
                    if next_project:
                        # Swap orders
                        project.order, next_project.order = next_project.order, project.order
                        project.save()
                        next_project.save()
                        return Response({'message': 'Project moved down successfully'})
                    else:
                        return Response({'error': 'Project is already last'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({'error': 'Invalid direction or new_order parameter'}, status=status.HTTP_400_BAD_REQUEST)


class AdminServiceViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for services without pagination.
    Used by the admin dashboard to display all services.
    """
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order']
    ordering = ['order', 'name']
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """Optimized queryset with prefetching to avoid N+1 queries"""
        return Service.objects.select_related().prefetch_related(
            'categories',
            'subcategories',
            'album_images'
        ).annotate(
            album_images_count_annotated=models.Count('album_images')
        ).order_by('order', 'name')

    def get_serializer_context(self):
        """Add request to serializer context so it can build absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # Capture original filename from uploaded icon
        icon_file = self.request.FILES.get('icon')
        
        # Save the service with the icon filename if provided
        if icon_file:
            serializer.save(original_filename=icon_file.name)
        else:
            serializer.save()

    def perform_update(self, serializer):
        # Capture original filename from uploaded icon if a new one is provided
        icon_file = self.request.FILES.get('icon')
        if icon_file:
            serializer.save(original_filename=icon_file.name)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reorder(self, request, pk=None):
        """
        Reorder services. Accepts 'direction' (up/down) or 'new_order' parameter.
        """
        service = self.get_object()
        direction = request.data.get('direction')
        new_order = request.data.get('new_order')
        
        if new_order is not None:
            # Direct order assignment
            try:
                new_order = int(new_order)
                with transaction.atomic():
                    old_order = service.order or 0
                    
                    if new_order > old_order:
                        # Moving down: shift items up
                        Service.objects.filter(
                            order__gt=old_order,
                            order__lte=new_order
                        ).update(order=models.F('order') - 1)
                    elif new_order < old_order:
                        # Moving up: shift items down
                        Service.objects.filter(
                            order__gte=new_order,
                            order__lt=old_order
                        ).update(order=models.F('order') + 1)
                    
                    service.order = new_order
                    service.save()
                
                return Response({'message': 'Service reordered successfully'})
            except ValueError:
                return Response({'error': 'Invalid order value'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif direction in ['up', 'down']:
            # Up/down arrow functionality
            with transaction.atomic():
                if direction == 'up':
                    # Find the service with the order just before this one
                    previous_service = Service.objects.filter(
                        order__lt=service.order or 0
                    ).order_by('-order').first()
                    
                    if previous_service:
                        # Swap orders
                        service.order, previous_service.order = previous_service.order, service.order
                        service.save()
                        previous_service.save()
                        return Response({'message': 'Service moved up successfully'})
                    else:
                        return Response({'error': 'Service is already first'}, status=status.HTTP_400_BAD_REQUEST)
                
                else:  # direction == 'down'
                    # Find the service with the order just after this one
                    next_service = Service.objects.filter(
                        order__gt=service.order or 0
                    ).order_by('order').first()
                    
                    if next_service:
                        # Swap orders
                        service.order, next_service.order = next_service.order, service.order
                        service.save()
                        next_service.save()
                        return Response({'message': 'Service moved down successfully'})
                    else:
                        return Response({'error': 'Service is already last'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({'error': 'Invalid direction or new_order parameter'}, status=status.HTTP_400_BAD_REQUEST)