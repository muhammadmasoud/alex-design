from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory
from .category_serializers import (
    ProjectCategorySerializer, ProjectSubcategorySerializer,
    ServiceCategorySerializer, ServiceSubcategorySerializer
)

class ProjectCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination to show all categories
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get all subcategories for this category"""
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = ProjectSubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete to check if category or its subcategories have projects"""
        category = self.get_object()
        project_count = category.projects.count()
        
        # Also check if any subcategories have projects
        subcategory_project_count = sum(
            subcat.projects.count() 
            for subcat in category.subcategories.all()
        )
        
        total_project_count = project_count + subcategory_project_count
        
        if total_project_count > 0:
            subcategory_count = category.subcategories.count()
            message_parts = []
            
            if project_count > 0:
                message_parts.append(f'{project_count} project(s) directly associated')
            
            if subcategory_project_count > 0:
                message_parts.append(f'{subcategory_project_count} project(s) in its subcategories')
            
            message = f'Cannot delete category. It has {" and ".join(message_parts)} with it.'
            
            if subcategory_count > 0:
                message += f' Deleting this category would also delete {subcategory_count} subcategory(ies).'
            
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

class ProjectSubcategoryViewSet(viewsets.ModelViewSet):
    queryset = ProjectSubcategory.objects.all()
    serializer_class = ProjectSubcategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination to show all subcategories
    
    def get_queryset(self):
        queryset = ProjectSubcategory.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete to check if subcategory has projects"""
        subcategory = self.get_object()
        project_count = subcategory.projects.count()
        
        if project_count > 0:
            return Response({
                'error': f'Cannot delete subcategory. It has {project_count} project(s) associated with it.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination to show all categories
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get all subcategories for this category"""
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = ServiceSubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete to check if category or its subcategories have services"""
        category = self.get_object()
        service_count = category.services.count()
        
        # Also check if any subcategories have services
        subcategory_service_count = sum(
            subcat.services.count() 
            for subcat in category.subcategories.all()
        )
        
        total_service_count = service_count + subcategory_service_count
        
        if total_service_count > 0:
            subcategory_count = category.subcategories.count()
            message_parts = []
            
            if service_count > 0:
                message_parts.append(f'{service_count} service(s) directly associated')
            
            if subcategory_service_count > 0:
                message_parts.append(f'{subcategory_service_count} service(s) in its subcategories')
            
            message = f'Cannot delete category. It has {" and ".join(message_parts)} with it.'
            
            if subcategory_count > 0:
                message += f' Deleting this category would also delete {subcategory_count} subcategory(ies).'
            
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

class ServiceSubcategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceSubcategory.objects.all()
    serializer_class = ServiceSubcategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination to show all subcategories
    
    def get_queryset(self):
        queryset = ServiceSubcategory.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete to check if subcategory has services"""
        subcategory = self.get_object()
        service_count = subcategory.services.count()
        
        if service_count > 0:
            return Response({
                'error': f'Cannot delete subcategory. It has {service_count} service(s) associated with it.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
