from django.db import models
import os
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from PIL import Image
import io

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
    Validate uploaded image file
    """
    try:
        # Check file size (25MB max)
        if image.size > 25 * 1024 * 1024:
            raise ValidationError("Image file too large. Maximum size is 25MB.")
        
        # Check if file is a valid image
        img = Image.open(image)
        img.verify()
        
        # Check format
        valid_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'BMP', 'WEBP', 'TIFF']
        if img.format not in valid_formats:
            raise ValidationError(f"Unsupported image format. Supported formats: {', '.join(valid_formats)}")
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError("Invalid image file.")

def project_image_upload_path(instance, filename):
    """
    Custom upload path for project images.
    Creates a filename based on project title to avoid duplicates.
    """
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Create filename based on project title
    if instance.title:
        filename = f"{slugify(instance.title)}.{ext}"
    else:
        filename = f"project_{instance.pk or 'new'}.{ext}"
    
    # Full path
    upload_path = f"projects/{filename}"
    
    # If file already exists, delete it to replace with new one
    if default_storage.exists(upload_path):
        default_storage.delete(upload_path)
    
    return upload_path

def service_icon_upload_path(instance, filename):
    """
    Custom upload path for service icons.
    Creates a filename based on service name to avoid duplicates.
    """
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Create filename based on service name
    if instance.name:
        filename = f"{slugify(instance.name)}.{ext}"
    else:
        filename = f"service_{instance.pk or 'new'}.{ext}"
    
    # Full path
    upload_path = f"services/{filename}"
    
    # If file already exists, delete it to replace with new one
    if default_storage.exists(upload_path):
        default_storage.delete(upload_path)
    
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
        # Delete old image if updating
        if self.pk:
            try:
                old_instance = Project.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
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
        # Delete old icon if updating
        if self.pk:
            try:
                old_instance = Service.objects.get(pk=self.pk)
                if old_instance.icon and old_instance.icon != self.icon:
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
