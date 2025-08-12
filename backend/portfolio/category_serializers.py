from rest_framework import serializers
from .models import ProjectCategory, ProjectSubcategory, ServiceCategory, ServiceSubcategory

class ProjectCategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()
    subcategories_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectCategory
        fields = ['id', 'name', 'description', 'created_at', 'subcategories_count', 'subcategories_names']
    
    def get_subcategories_count(self, obj):
        return obj.subcategories.count()
    
    def get_subcategories_names(self, obj):
        return [sub.name for sub in obj.subcategories.all()]

class ProjectSubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ProjectSubcategory
        fields = ['id', 'name', 'description', 'category', 'category_name', 'created_at']

class ServiceCategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()
    subcategories_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'created_at', 'subcategories_count', 'subcategories_names']
    
    def get_subcategories_count(self, obj):
        return obj.subcategories.count()
    
    def get_subcategories_names(self, obj):
        return [sub.name for sub in obj.subcategories.all()]

class ServiceSubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ServiceSubcategory
        fields = ['id', 'name', 'description', 'category', 'category_name', 'created_at']
