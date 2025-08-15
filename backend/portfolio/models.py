from django.db import models
import os
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from PIL import Image
import io
# Register HEIF opener for iPhone photos
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # If pillow-heif is not installed, HEIC support won't work

# Dynamic Category Models
class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Project Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ProjectSubcategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Project Subcategories"
        unique_together = ['name', 'category']
        ordering = ['category__name', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ServiceSubcategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Subcategories"
        unique_together = ['name', 'category']
        ordering = ['category__name', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

def validate_image(image):
    """
    Validate uploaded image file - handles iPhone HEIC and other formats
    """
    try:
        # Check file size (25MB max)
        if image.size > 25 * 1024 * 1024:
            raise ValidationError("Image file too large. Maximum size is 25MB.")
        
        # Reset file pointer
        image.seek(0)
        
        # Try to open and validate the image
        try:
            img = Image.open(image)
            
            # Handle iPhone HEIC files and convert them
            if img.format == 'HEIF' or image.name.lower().endswith(('.heic', '.heif')):
                # Convert HEIC to JPEG
                rgb_img = img.convert('RGB')
                # Save converted image back to the same file object
                image.seek(0)
                rgb_img.save(image, format='JPEG', quality=85)
                image.seek(0)
                img = Image.open(image)
            
            # Check for supported formats (more inclusive)
            valid_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'BMP', 'WEBP', 'TIFF', 'HEIF']
            if img.format and img.format not in valid_formats:
                raise ValidationError(f"Unsupported image format: {img.format}. Supported formats: JPEG, PNG, GIF, BMP, WebP, TIFF")
            
            # Verify the image can be processed
            img.verify()
            
        except Exception as img_error:
            # If PIL fails, try to give a more specific error
            error_msg = str(img_error).lower()
            if 'heif' in error_msg or 'heic' in error_msg:
                raise ValidationError("HEIC/HEIF format detected. Please convert to JPEG or PNG, or use a different photo.")
            elif 'truncated' in error_msg:
                raise ValidationError("Image file appears to be corrupted or incomplete.")
            elif 'decode' in error_msg:
                raise ValidationError("Unable to decode image. Please try a different image format.")
            else:
                raise ValidationError(f"Invalid image file: {str(img_error)}")
            
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error processing image: {str(e)}")

def project_image_upload_path(instance, filename):
    """
    Custom upload path for project images.
    Creates a unique filename to avoid conflicts when updating.
    """
    import uuid
    from datetime import datetime
    
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Create unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if instance.title:
        base_name = slugify(instance.title)[:50]  # Limit length
        filename = f"{base_name}_{timestamp}_{unique_id}.{ext}"
    else:
        filename = f"project_{timestamp}_{unique_id}.{ext}"
    
    # Full path
    upload_path = f"projects/{filename}"
    
    return upload_path

def service_icon_upload_path(instance, filename):
    """
    Custom upload path for service icons.
    Creates a unique filename to avoid conflicts when updating.
    """
    import uuid
    from datetime import datetime
    
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Create unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if instance.name:
        base_name = slugify(instance.name)[:50]  # Limit length
        filename = f"{base_name}_{timestamp}_{unique_id}.{ext}"
    else:
        filename = f"service_{timestamp}_{unique_id}.{ext}"
    
    # Full path
    upload_path = f"services/{filename}"
    
    return upload_path

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=project_image_upload_path, null=True, blank=True, validators=[validate_image])
    
    # Category fields
    category = models.ForeignKey(
        ProjectCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='projects',
        help_text="Select the main category for this project"
    )
    subcategory = models.ForeignKey(
        ProjectSubcategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='projects',
        help_text="Select a subcategory (optional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_category_name(self):
        """Get category name"""
        if self.category:
            return self.category.name
        return None

    def get_subcategory_name(self):
        """Get subcategory name"""
        if self.subcategory:
            return self.subcategory.name
        return None

    def save(self, *args, **kwargs):
        # Delete old image if updating and a new image is provided
        if self.pk:
            try:
                old_instance = Project.objects.get(pk=self.pk)
                # Check if image field has changed and old image exists
                if (old_instance.image and 
                    hasattr(self.image, 'file') and 
                    self.image.file and 
                    old_instance.image.name != self.image.name):
                    # Delete the old image file
                    old_instance.image.delete(save=False)
            except Project.DoesNotExist:
                pass
        super().save(*args, **kwargs)
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to=service_icon_upload_path, null=True, blank=True, validators=[validate_image])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Service price in USD")
    
    # Category fields
    category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='services',
        help_text="Select the main category for this service"
    )
    subcategory = models.ForeignKey(
        ServiceSubcategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='services',
        help_text="Select a subcategory (optional)"
    )

    def __str__(self):
        return self.name

    def get_category_name(self):
        """Get category name"""
        if self.category:
            return self.category.name
        return None

    def get_subcategory_name(self):
        """Get subcategory name"""
        if self.subcategory:
            return self.subcategory.name
        return None

    def save(self, *args, **kwargs):
        # Delete old icon if updating and a new icon is provided
        if self.pk:
            try:
                old_instance = Service.objects.get(pk=self.pk)
                # Check if icon field has changed and old icon exists
                if (old_instance.icon and 
                    hasattr(self.icon, 'file') and 
                    self.icon.file and 
                    old_instance.icon.name != self.icon.name):
                    # Delete the old icon file
                    old_instance.icon.delete(save=False)
            except Service.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='portfolio_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='portfolio_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
