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
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'original_filename', 
                 'optimized_image', 'optimized_image_small', 'optimized_image_medium', 'optimized_image_large']
    
    def get_image_url(self, obj):
        """Get the optimized image URL from the database"""
        if obj.optimized_image_medium:
            # Use the medium optimized image if available
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image_medium.replace('\\', '/')}")
            return f"/media/{obj.optimized_image_medium.replace('\\', '/')}"
        elif obj.optimized_image:
            # Fallback to default optimized image
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image.replace('\\', '/')}")
            return f"/media/{obj.optimized_image.replace('\\', '/')}"
        elif obj.image:
            # Fallback to original if no optimized version exists
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs automatically"""
        representation = super().to_representation(instance)
        
        # Use optimized image URLs from database
        if instance.optimized_image_medium:
            representation['image'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
        elif instance.optimized_image:
            representation['image'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
        elif instance.image:
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
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'original_filename',
                 'optimized_image', 'optimized_image_small', 'optimized_image_medium', 'optimized_image_large']
    
    def get_image_url(self, obj):
        """Get the optimized image URL from the database"""
        if obj.optimized_image_medium:
            # Use the medium optimized image if available
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image_medium.replace('\\', '/')}")
            return f"/media/{obj.optimized_image_medium.replace('\\', '/')}"
        elif obj.optimized_image:
            # Fallback to default optimized image
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image.replace('\\', '/')}")
            return f"/media/{obj.optimized_image.replace('\\', '/')}"
        elif obj.image:
            # Fallback to original if no optimized version exists
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs automatically"""
        representation = super().to_representation(instance)
        # Use optimized image URLs from database
        if instance.optimized_image_medium:
            representation['image'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
        elif instance.optimized_image:
            representation['image'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
        elif instance.image:
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
        """Get the optimized image URL from the database"""
        if obj.optimized_image_medium:
            # Use the medium optimized image if available
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image_medium.replace('\\', '/')}")
            return f"/media/{obj.optimized_image_medium.replace('\\', '/')}"
        elif obj.optimized_image:
            # Fallback to default optimized image
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_image.replace('\\', '/')}")
            return f"/media/{obj.optimized_image.replace('\\', '/')}"
        elif obj.image:
            # Fallback to original if no optimized version exists
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
        """Custom representation to include optimized image URLs automatically"""
        representation = super().to_representation(instance)
        
        # Use optimized image URLs from database
        if instance.optimized_image_medium:
            representation['image'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image_medium.replace('\\', '/')}"
        elif instance.optimized_image:
            representation['image'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
            representation['image_url'] = f"/media/{instance.optimized_image.replace('\\', '/')}"
        elif instance.image:
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
        """Get the optimized icon URL from the database"""
        if obj.optimized_icon_medium:
            # Use the medium optimized icon if available
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_icon_medium.replace('\\', '/')}")
            return f"/media/{obj.optimized_icon_medium.replace('\\', '/')}"
        elif obj.optimized_icon:
            # Fallback to default optimized icon
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/media/{obj.optimized_icon.replace('\\', '/')}")
            return f"/media/{obj.optimized_icon.replace('\\', '/')}"
        elif obj.icon:
            # Fallback to original if no optimized version exists
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
        """Custom representation to include optimized icon URLs automatically"""
        representation = super().to_representation(instance)
        # Use optimized icon URLs from database
        if instance.optimized_icon_medium:
            representation['icon'] = f"/media/{instance.optimized_icon_medium}"
            representation['icon_url'] = f"/media/{instance.optimized_icon_medium}"
        elif instance.optimized_icon:
            representation['icon'] = f"/media/{instance.optimized_icon}"
            representation['icon_url'] = f"/media/{instance.optimized_icon}"
        elif instance.icon:
            representation['icon'] = instance.icon.url
            representation['icon_url'] = instance.icon.url
        else:
            representation['icon'] = None
            representation['icon_url'] = None
        return representation
