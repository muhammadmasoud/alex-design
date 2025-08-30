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
        try:
            # Safely check if optimized image paths exist and are valid
            if hasattr(obj, 'optimized_image_medium') and obj.optimized_image_medium and obj.optimized_image_medium.strip():
                # Use the medium optimized image if available
                request = self.context.get('request')
                if request:
                    # Ensure the path is properly formatted
                    clean_path = obj.optimized_image_medium.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_image_medium.replace('\\', '/').strip()}"
            elif hasattr(obj, 'optimized_image') and obj.optimized_image and obj.optimized_image.strip():
                # Fallback to default optimized image
                request = self.context.get('request')
                if request:
                    clean_path = obj.optimized_image.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_image.replace('\\', '/').strip()}"
            elif hasattr(obj, 'image') and obj.image:
                # Fallback to original if no optimized version exists
                try:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.image.url)
                    return obj.image.url
                except Exception:
                    # If URL building fails, return a safe fallback
                    return f"/media/{obj.image.name}" if obj.image.name else None
            return None
        except Exception as e:
            # If URL building fails, return a safe fallback
            print(f"Error building image URL for ProjectImage {getattr(obj, 'id', 'unknown')}: {e}")
            return None
    
    def to_representation(self, instance):
        """
        Custom representation to handle edge cases and prevent serialization errors
        """
        try:
            representation = super().to_representation(instance)
            
            # Safely handle image URLs with better error handling
            try:
                if hasattr(instance, 'optimized_image_medium') and instance.optimized_image_medium and instance.optimized_image_medium.strip():
                    clean_path = instance.optimized_image_medium.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'optimized_image') and instance.optimized_image and instance.optimized_image.strip():
                    clean_path = instance.optimized_image.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'image') and instance.image:
                    try:
                        representation['image'] = instance.image.url
                        representation['image_url'] = instance.image.url
                    except Exception:
                        # Fallback to media path if URL building fails
                        representation['image'] = f"/media/{instance.image.name}" if instance.image.name else None
                        representation['image_url'] = f"/media/{instance.image.name}" if instance.image.name else None
                else:
                    representation['image'] = None
                    representation['image_url'] = None
            except Exception as e:
                # If image URL handling fails, set safe defaults
                print(f"Error handling image URLs for ProjectImage {getattr(instance, 'id', 'unknown')}: {e}")
                representation['image'] = None
                representation['image_url'] = None
            
            return representation
        except Exception as e:
            # If representation fails completely, return a safe fallback
            print(f"Error in to_representation for ProjectImage {getattr(instance, 'id', 'unknown')}: {e}")
            return {
                'id': getattr(instance, 'id', None),
                'image': None,
                'image_url': None,
                'title': getattr(instance, 'title', None),
                'description': getattr(instance, 'description', None),
                'order': getattr(instance, 'order', 0),
                'original_filename': getattr(instance, 'original_filename', None),
                'optimized_image': None,
                'optimized_image_small': None,
                'optimized_image_medium': None,
                'optimized_image_large': None
            }

class ServiceImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'original_filename',
                 'optimized_image', 'optimized_image_small', 'optimized_image_medium', 'optimized_image_large']
    
    def get_image_url(self, obj):
        """Get the optimized image URL from the database"""
        try:
            # Safely check if optimized image paths exist and are valid
            if hasattr(obj, 'optimized_image_medium') and obj.optimized_image_medium and obj.optimized_image_medium.strip():
                # Use the medium optimized image if available
                request = self.context.get('request')
                if request:
                    # Ensure the path is properly formatted
                    clean_path = obj.optimized_image_medium.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_image_medium.replace('\\', '/').strip()}"
            elif hasattr(obj, 'optimized_image') and obj.optimized_image and obj.optimized_image.strip():
                # Fallback to default optimized image
                request = self.context.get('request')
                if request:
                    clean_path = obj.optimized_image.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_image.replace('\\', '/').strip()}"
            elif hasattr(obj, 'image') and obj.image:
                # Fallback to original if no optimized version exists
                try:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.image.url)
                    return obj.image.url
                except Exception:
                    # If URL building fails, return a safe fallback
                    return f"/media/{obj.image.name}" if obj.image.name else None
            return None
        except Exception as e:
            # If URL building fails, return a safe fallback
            print(f"Error building image URL for ServiceImage {getattr(obj, 'id', 'unknown')}: {e}")
            return None
    
    def to_representation(self, instance):
        """
        Custom representation to handle edge cases and prevent serialization errors
        """
        try:
            representation = super().to_representation(instance)
            
            # Safely handle image URLs with better error handling
            try:
                if hasattr(instance, 'optimized_image_medium') and instance.optimized_image_medium and instance.optimized_image_medium.strip():
                    clean_path = instance.optimized_image_medium.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'optimized_image') and instance.optimized_image and instance.optimized_image.strip():
                    clean_path = instance.optimized_image.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'image') and instance.image:
                    try:
                        representation['image'] = instance.image.url
                        representation['image_url'] = instance.image.url
                    except Exception:
                        # Fallback to media path if URL building fails
                        representation['image'] = f"/media/{instance.image.name}" if instance.image.name else None
                        representation['image_url'] = f"/media/{instance.image.name}" if instance.image.name else None
                else:
                    representation['image'] = None
                    representation['image_url'] = None
            except Exception as e:
                # If image URL handling fails, set safe defaults
                print(f"Error handling image URLs for ServiceImage {getattr(instance, 'id', 'unknown')}: {e}")
                representation['image'] = None
                representation['image_url'] = None
            
            return representation
        except Exception as e:
            # If representation fails completely, return a safe fallback
            print(f"Error in to_representation for ServiceImage {getattr(instance, 'id', 'unknown')}: {e}")
            return {
                'id': getattr(instance, 'id', None),
                'image': None,
                'image_url': None,
                'title': getattr(instance, 'title', None),
                'description': getattr(instance, 'description', None),
                'order': getattr(instance, 'order', 0),
                'original_filename': getattr(instance, 'original_filename', None),
                'optimized_image': None,
                'optimized_image_small': None,
                'optimized_image_medium': None,
                'optimized_image_large': None
            }

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
        try:
            if hasattr(obj, 'optimized_image_medium') and obj.optimized_image_medium:
                # Use the medium optimized image if available
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(f"/media/{obj.optimized_image_medium.replace('\\', '/')}")
                return f"/media/{obj.optimized_image_medium.replace('\\', '/')}"
            elif hasattr(obj, 'optimized_image') and obj.optimized_image:
                # Fallback to default optimized image
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(f"/media/{obj.optimized_image.replace('\\', '/')}")
                return f"/media/{obj.optimized_image.replace('\\', '/')}"
            elif hasattr(obj, 'image') and obj.image:
                # Fallback to original if no optimized version exists
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            return None
        except Exception as e:
            # If URL building fails, return a safe fallback
            print(f"Error building image URL for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return None
    
    def get_category_name(self, obj):
        """Get category name"""
        try:
            return obj.get_category_name()
        except Exception as e:
            print(f"Error getting category name for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return ""
    
    def get_subcategory_name(self, obj):
        """Get subcategory name"""
        try:
            return obj.get_subcategory_name()
        except Exception as e:
            print(f"Error getting subcategory name for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return ""
    
    def get_category_names(self, obj):
        """Get all category names as a list"""
        try:
            return obj.get_category_names()
        except Exception as e:
            print(f"Error getting category names for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return []

    def get_subcategory_names(self, obj):
        """Get all subcategory names as a list"""
        try:
            return obj.get_subcategory_names()
        except Exception as e:
            print(f"Error getting subcategory names for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return []
    
    def get_album_images_count(self, obj):
        """Get the count of album images - optimized to avoid extra queries"""
        try:
            # Use the annotation if available, otherwise fallback to count
            return getattr(obj, 'album_images_count_annotated', obj.album_images.count())
        except Exception as e:
            print(f"Error getting album images count for Project {getattr(obj, 'id', 'unknown')}: {e}")
            return 0
    
    def get_featured_album_images(self, obj):
        """Get first few album images for preview - optimized"""
        try:
            # Use prefetched data if available to avoid N+1 queries
            if hasattr(obj, '_prefetched_objects_cache') and 'album_images' in obj._prefetched_objects_cache:
                featured_images = list(obj.album_images.all()[:6])  # Limit to 6 for performance
            else:
                featured_images = obj.album_images.all()[:6]
            
            # Safely serialize with error handling
            try:
                return ProjectImageSerializer(featured_images, many=True, context=self.context).data
            except Exception as e:
                print(f"Error serializing featured album images for project {getattr(obj, 'id', 'unknown')}: {e}")
                # Return empty list if serialization fails
                return []
        except Exception as e:
            print(f"Error getting featured album images for project {getattr(obj, 'id', 'unknown')}: {e}")
            return []
    
    def to_representation(self, instance):
        """Custom representation to include optimized image URLs automatically"""
        try:
            representation = super().to_representation(instance)
            
            # Safely handle image URLs with better error handling
            try:
                if hasattr(instance, 'optimized_image_medium') and instance.optimized_image_medium and instance.optimized_image_medium.strip():
                    clean_path = instance.optimized_image_medium.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'optimized_image') and instance.optimized_image and instance.optimized_image.strip():
                    clean_path = instance.optimized_image.replace('\\', '/').strip()
                    if clean_path:
                        representation['image'] = f"/media/{clean_path}"
                        representation['image_url'] = f"/media/{clean_path}"
                    else:
                        representation['image'] = None
                        representation['image_url'] = None
                elif hasattr(instance, 'image') and instance.image:
                    try:
                        representation['image'] = instance.image.url
                        representation['image_url'] = instance.image.url
                    except Exception:
                        # Fallback to media path if URL building fails
                        representation['image'] = f"/media/{instance.image.name}" if instance.image.name else None
                        representation['image_url'] = f"/media/{instance.image.name}" if instance.image.name else None
                else:
                    representation['image'] = None
                    representation['image_url'] = None
            except Exception as e:
                # If image URL handling fails, set safe defaults
                print(f"Error handling image URLs for Project {getattr(instance, 'id', 'unknown')}: {e}")
                representation['image'] = None
                representation['image_url'] = None
            
            return representation
        except Exception as e:
            # If representation fails completely, return a safe fallback
            print(f"Error in to_representation for Project {getattr(instance, 'id', 'unknown')}: {e}")
            return {
                'id': getattr(instance, 'id', None),
                'title': getattr(instance, 'title', ''),
                'description': getattr(instance, 'description', ''),
                'image': None,
                'image_url': None,
                'category_names': [],
                'subcategory_names': [],
                'album_images_count': 0,
                'featured_album_images': [],
                'project_date': getattr(instance, 'project_date', None),
                'order': getattr(instance, 'order', 0)
            }


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
        try:
            # Safely check if optimized icon paths exist and are valid
            if hasattr(obj, 'optimized_icon_medium') and obj.optimized_icon_medium and obj.optimized_icon_medium.strip():
                # Use the medium optimized icon if available
                request = self.context.get('request')
                if request:
                    # Ensure the path is properly formatted
                    clean_path = obj.optimized_icon_medium.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_icon_medium.replace('\\', '/').strip()}"
            elif hasattr(obj, 'optimized_icon') and obj.optimized_icon and obj.optimized_icon.strip():
                # Fallback to default optimized icon
                request = self.context.get('request')
                if request:
                    clean_path = obj.optimized_icon.replace('\\', '/').strip()
                    if clean_path:
                        return request.build_absolute_uri(f"/media/{clean_path}")
                return f"/media/{obj.optimized_icon.replace('\\', '/').strip()}"
            elif hasattr(obj, 'icon') and obj.icon:
                # Fallback to original if no optimized version exists
                try:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.icon.url)
                    return obj.icon.url
                except Exception:
                    # If URL building fails, return a safe fallback
                    return f"/media/{obj.icon.name}" if obj.icon.name else None
            return None
        except Exception as e:
            # If URL building fails, return a safe fallback
            print(f"Error building icon URL for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return None

    def get_category_names(self, obj):
        """Get all category names as a list"""
        try:
            return obj.get_category_names()
        except Exception as e:
            print(f"Error getting category names for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return []

    def get_subcategory_names(self, obj):
        """Get all subcategory names as a list"""
        try:
            return obj.get_subcategory_names()
        except Exception as e:
            print(f"Error getting subcategory names for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return []
    
    def get_category_name(self, obj):
        """Get first category name for backward compatibility"""
        try:
            return obj.get_category_name()
        except Exception as e:
            print(f"Error getting category name for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return ""
    
    def get_subcategory_name(self, obj):
        """Get first subcategory name for backward compatibility"""
        try:
            return obj.get_subcategory_name()
        except Exception as e:
            print(f"Error getting subcategory name for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return ""
    
    def get_album_images_count(self, obj):
        """Get the count of album images - optimized to avoid extra queries"""
        try:
            return getattr(obj, 'album_images_count_annotated', obj.album_images.count())
        except Exception as e:
            print(f"Error getting album images count for Service {getattr(obj, 'id', 'unknown')}: {e}")
            return 0
    
    def get_featured_album_images(self, obj):
        """Get all album images for preview - optimized"""
        try:
            # Use prefetched data if available to avoid N+1 queries
            if hasattr(obj, '_prefetched_objects_cache') and 'album_images' in obj._prefetched_objects_cache:
                featured_images = list(obj.album_images.all()[:6])  # Limit to 6 for performance
            else:
                featured_images = obj.album_images.all()[:6]
            
            # Safely serialize with error handling
            try:
                return ServiceImageSerializer(featured_images, many=True, context=self.context).data
            except Exception as e:
                print(f"Error serializing featured album images for service {getattr(obj, 'id', 'unknown')}: {e}")
                # Return empty list if serialization fails
                return []
        except Exception as e:
            print(f"Error getting featured album images for service {getattr(obj, 'id', 'unknown')}: {e}")
            return []
    
    def to_representation(self, instance):
        """Custom representation to include optimized icon URLs automatically"""
        try:
            representation = super().to_representation(instance)
            
            # Safely handle icon URLs with better error handling
            try:
                if hasattr(instance, 'optimized_icon_medium') and instance.optimized_icon_medium and instance.optimized_icon_medium.strip():
                    clean_path = instance.optimized_icon_medium.replace('\\', '/').strip()
                    if clean_path:
                        representation['icon'] = f"/media/{clean_path}"
                        representation['icon_url'] = f"/media/{clean_path}"
                    else:
                        representation['icon'] = None
                        representation['icon_url'] = None
                elif hasattr(instance, 'optimized_icon') and instance.optimized_icon and instance.optimized_icon.strip():
                    clean_path = instance.optimized_icon.replace('\\', '/').strip()
                    if clean_path:
                        representation['icon'] = f"/media/{clean_path}"
                        representation['icon_url'] = f"/media/{clean_path}"
                    else:
                        representation['icon'] = None
                        representation['icon_url'] = None
                elif hasattr(instance, 'icon') and instance.icon:
                    try:
                        representation['icon'] = instance.icon.url
                        representation['icon_url'] = instance.icon.url
                    except Exception:
                        # Fallback to media path if URL building fails
                        representation['icon'] = f"/media/{instance.icon.name}" if instance.icon.name else None
                        representation['icon_url'] = f"/media/{instance.icon.name}" if instance.icon.name else None
                else:
                    representation['icon'] = None
                    representation['icon_url'] = None
            except Exception as e:
                # If icon URL handling fails, set safe defaults
                print(f"Error handling icon URLs for Service {getattr(instance, 'id', 'unknown')}: {e}")
                representation['icon'] = None
                representation['icon_url'] = None
            
            return representation
        except Exception as e:
            # If representation fails completely, return a safe fallback
            print(f"Error in to_representation for Service {getattr(instance, 'id', 'unknown')}: {e}")
            return {
                'id': getattr(instance, 'id', None),
                'name': getattr(instance, 'name', ''),
                'description': getattr(instance, 'description', ''),
                'icon': None,
                'icon_url': None,
                'price': str(getattr(instance, 'price', 0)),
                'category_names': [],
                'subcategory_names': [],
                'album_images_count': 0,
                'featured_album_images': [],
                'order': getattr(instance, 'order', 0)
            }
