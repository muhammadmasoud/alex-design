from rest_framework import serializers
from .models import Project, Service, ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory

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

class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # For reading the full URL
    category_name = serializers.SerializerMethodField()
    subcategory_name = serializers.SerializerMethodField()
    category_obj = ProjectCategorySimpleSerializer(source='category', read_only=True)
    subcategory_obj = ProjectSubcategorySimpleSerializer(source='subcategory', read_only=True)
    
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


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    subcategory_name = serializers.SerializerMethodField()
    category_obj = ServiceCategorySimpleSerializer(source='category', read_only=True)
    subcategory_obj = ServiceSubcategorySimpleSerializer(source='subcategory', read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'
    
    def get_category_name(self, obj):
        """Get category name"""
        return obj.get_category_name()
    
    def get_subcategory_name(self, obj):
        """Get subcategory name"""
        return obj.get_subcategory_name()
    
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
