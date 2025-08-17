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
    thumbnail_url = serializers.SerializerMethodField()
    medium_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'image_url', 'thumbnail_url', 'medium_url', 'title', 'description', 'order', 'created_at']
    
    def get_image_url(self, obj):
        """Get the full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get the thumbnail URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
    
    def get_medium_url(self, obj):
        """Get the medium size URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.medium.url)
            return obj.medium.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs"""
        representation = super().to_representation(instance)
        
        # Provide multiple image sizes for responsive loading
        if instance.image:
            request = self.context.get('request')
            if request:
                # Use thumbnail for list views, medium for details
                representation['image'] = request.build_absolute_uri(instance.medium.url)
                representation['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
                representation['full_size'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.medium.url
                representation['thumbnail'] = instance.thumbnail.url
                representation['full_size'] = instance.image.url
        else:
            representation['image'] = None
            representation['thumbnail'] = None
            representation['full_size'] = None
        return representation

class ServiceImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'created_at']
    
    def get_image_url(self, obj):
        """Get the full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include both image field and image_url"""
        representation = super().to_representation(instance)
        # Keep the original image field for the frontend, but also provide image_url
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.image.url
        else:
            representation['image'] = None
        return representation

class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # For reading the full URL
    thumbnail_url = serializers.SerializerMethodField()
    medium_url = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    subcategory_name = serializers.SerializerMethodField()
    category_obj = ProjectCategorySimpleSerializer(source='category', read_only=True)
    subcategory_obj = ProjectSubcategorySimpleSerializer(source='subcategory', read_only=True)
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
    
    def get_thumbnail_url(self, obj):
        """Get the thumbnail URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
    
    def get_medium_url(self, obj):
        """Get the medium size URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.medium.url)
            return obj.medium.url
        return None
    
    def get_category_name(self, obj):
        """Get category name"""
        return obj.get_category_name()
    
    def get_subcategory_name(self, obj):
        """Get subcategory name"""
        return obj.get_subcategory_name()
    
    def get_album_images_count(self, obj):
        """Get the count of album images - optimized to avoid extra queries"""
        # Use the annotation if available, otherwise fallback to count
        return getattr(obj, 'album_images_count_annotated', obj.album_images.count())
    
    def get_featured_album_images(self, obj):
        """Get first few album images for preview - optimized"""
        # Use prefetched data if available
        if hasattr(obj, 'prefetched_featured_images'):
            featured_images = obj.prefetched_featured_images
        else:
            featured_images = obj.album_images.all()[:4]
        return ProjectImageSerializer(featured_images, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs"""
        representation = super().to_representation(instance)
        
        # Use thumbnail for card views to improve loading speed
        if instance.image:
            request = self.context.get('request')
            if request:
                # Default to medium size for main image
                representation['image'] = request.build_absolute_uri(instance.medium.url)
                representation['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
                representation['full_size'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.medium.url
                representation['thumbnail'] = instance.thumbnail.url
                representation['full_size'] = instance.image.url
        else:
            representation['image'] = None
            representation['thumbnail'] = None
            representation['full_size'] = None
        return representation


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    subcategory_name = serializers.SerializerMethodField()
    category_obj = ServiceCategorySimpleSerializer(source='category', read_only=True)
    subcategory_obj = ServiceSubcategorySimpleSerializer(source='subcategory', read_only=True)
    album_images_count = serializers.SerializerMethodField()
    featured_album_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = '__all__'
    
    def get_category_name(self, obj):
        """Get category name"""
        return obj.get_category_name()
    
    def get_subcategory_name(self, obj):
        """Get subcategory name"""
        return obj.get_subcategory_name()
    
    def get_album_images_count(self, obj):
        """Get the count of album images"""
        return obj.get_album_images_count()
    
    def get_featured_album_images(self, obj):
        """Get first few album images for preview"""
        featured_images = obj.get_featured_album_images(limit=4)
        return ServiceImageSerializer(featured_images, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Custom representation to include both icon field and icon_url"""
        representation = super().to_representation(instance)
        # Keep the original icon field for the frontend, but also provide icon_url
        if instance.icon:
            request = self.context.get('request')
            if request:
                representation['icon'] = request.build_absolute_uri(instance.icon.url)
            else:
                representation['icon'] = instance.icon.url
        else:
            representation['icon'] = None
        return representation
