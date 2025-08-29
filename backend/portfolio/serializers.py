from rest_framework import serializers
from .models import (
    Project, Service, ProjectCategory, ProjectSubcategory, 
    ServiceCategory, ServiceSubcategory, ProjectImage, ServiceImage
)

class ProjectCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id', 'name']

class ProjectSubcategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubcategory
        fields = ['id', 'name']

class ServiceCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']

class ServiceSubcategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSubcategory
        fields = ['id', 'name']

class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'original_filename']
    
    def get_image_url(self, obj):
        """Get the full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs"""
        representation = super().to_representation(instance)
        
        # Provide full URL for image field
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
                representation['image_url'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.image.url
                representation['image_url'] = instance.image.url
        else:
            representation['image'] = None
            representation['image_url'] = None
        return representation

class ServiceImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'original_filename']
    
    def get_image_url(self, obj):
        """Get the full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include full URLs"""
        representation = super().to_representation(instance)
        # Keep the original image field for the frontend, but also provide image_url
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
                representation['image_url'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.image.url
                representation['image_url'] = instance.image.url
        else:
            representation['image'] = None
            representation['image_url'] = None
        return representation

class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # For reading the full URL
    category_names = serializers.SerializerMethodField()
    subcategory_names = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()  # For backward compatibility
    subcategory_name = serializers.SerializerMethodField()  # For backward compatibility
    category_objs = ProjectCategorySimpleSerializer(source='categories', many=True, read_only=True)
    subcategory_objs = ProjectSubcategorySimpleSerializer(source='subcategories', many=True, read_only=True)
    album_images_count = serializers.SerializerMethodField()
    featured_album_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_image_url(self, obj):
        """Get the full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_category_name(self, obj):
        """Get category name"""
        return obj.get_category_name()
    
    def get_subcategory_name(self, obj):
        """Get subcategory name"""
        return obj.get_subcategory_name()
    
    def get_category_names(self, obj):
        """Get all category names as a list"""
        return obj.get_category_names()

    def get_subcategory_names(self, obj):
        """Get all subcategory names as a list"""
        return obj.get_subcategory_names()
    
    def get_album_images_count(self, obj):
        """Get the count of album images - optimized to avoid extra queries"""
        # Use the annotation if available, otherwise fallback to count
        return getattr(obj, 'album_images_count_annotated', obj.album_images.count())
    
    def get_featured_album_images(self, obj):
        """Get first few album images for preview - optimized"""
        # Use prefetched data if available to avoid N+1 queries
        if hasattr(obj, '_prefetched_objects_cache') and 'album_images' in obj._prefetched_objects_cache:
            featured_images = list(obj.album_images.all()[:6])  # Limit to 6 for performance
        else:
            featured_images = obj.album_images.all()[:6]
        return ProjectImageSerializer(featured_images, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs"""
        representation = super().to_representation(instance)
        
        # Provide full URL for image field
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
                representation['image_url'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.image.url
                representation['image_url'] = instance.image.url
        else:
            representation['image'] = None
            representation['image_url'] = None
        return representation


class ServiceSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    category_names = serializers.SerializerMethodField()
    subcategory_names = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()  # For backward compatibility
    subcategory_name = serializers.SerializerMethodField()  # For backward compatibility
    category_objs = ServiceCategorySimpleSerializer(source='categories', many=True, read_only=True)
    subcategory_objs = ServiceSubcategorySimpleSerializer(source='subcategories', many=True, read_only=True)
    album_images_count = serializers.SerializerMethodField()
    featured_album_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = '__all__'
    
    def get_icon_url(self, obj):
        """Get the optimized icon URL"""
        if obj.icon:
            # Use the optimized image URL from the model
            optimized_url = obj.get_optimized_image_url(size='lg', format='webp', quality='high')
            if optimized_url:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(optimized_url)
                return optimized_url
            # Fallback to original if optimization fails
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
    
    def get_category_names(self, obj):
        """Get all category names as a list"""
        return obj.get_category_names()

    def get_subcategory_names(self, obj):
        """Get all subcategory names as a list"""
        return obj.get_subcategory_names()
    
    def get_category_name(self, obj):
        """Get first category name for backward compatibility"""
        return obj.get_category_name()
    
    def get_subcategory_name(self, obj):
        """Get first subcategory name for backward compatibility"""
        return obj.get_subcategory_name()
    
    def get_album_images_count(self, obj):
        """Get the count of album images - optimized to avoid extra queries"""
        return getattr(obj, 'album_images_count_annotated', obj.album_images.count())
    
    def get_featured_album_images(self, obj):
        """Get all album images for preview - optimized"""
        # Use prefetched data if available to avoid N+1 queries
        if hasattr(obj, '_prefetched_objects_cache') and 'album_images' in obj._prefetched_objects_cache:
            featured_images = list(obj.album_images.all()[:6])  # Limit to 6 for performance
        else:
            featured_images = obj.album_images.all()[:6]
        return ServiceImageSerializer(featured_images, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Custom representation to include both icon field and icon_url"""
        representation = super().to_representation(instance)
        # Use optimized icon URLs for better quality
        if instance.icon:
            # Try to get optimized URL first
            optimized_url = instance.get_optimized_image_url(size='lg', format='webp', quality='high')
            if optimized_url:
                request = self.context.get('request')
                if request:
                    representation['icon'] = request.build_absolute_uri(optimized_url)
                    representation['icon_url'] = request.build_absolute_uri(optimized_url)
                else:
                    representation['icon'] = optimized_url
                    representation['icon_url'] = optimized_url
            else:
                # Fallback to original if optimization fails
                request = self.context.get('request')
                if request:
                    representation['icon'] = request.build_absolute_uri(instance.icon.url)
                    representation['icon_url'] = request.build_absolute_uri(instance.icon.url)
                else:
                    representation['icon'] = instance.icon.url
                    representation['icon_url'] = instance.icon.url
        else:
            representation['icon'] = None
            representation['icon_url'] = None
        return representation
