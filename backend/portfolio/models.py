from django.db import models
import os
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from PIL import Image
import io
from .consolidated_image_optimizer import optimize_uploaded_image, get_responsive_image_urls
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

def project_album_image_upload_path(instance, filename):
    """
    Custom upload path for project album images.
    Creates a unique filename to avoid conflicts when updating.
    """
    import uuid
    from datetime import datetime
    
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Create unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if instance.project.title:
        base_name = slugify(instance.project.title)[:50]  # Limit length
        filename = f"{base_name}_album_{timestamp}_{unique_id}.{ext}"
    else:
        filename = f"project_album_{timestamp}_{unique_id}.{ext}"
    
    # Full path
    upload_path = f"projects/albums/{filename}"
    
    return upload_path

def service_album_image_upload_path(instance, filename):
    """
    Custom upload path for service album images.
    Creates a unique filename to avoid conflicts when updating.
    """
    import uuid
    from datetime import datetime
    
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Create unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if instance.service.name:
        base_name = slugify(instance.service.name)[:50]  # Limit length
        filename = f"{base_name}_album_{timestamp}_{unique_id}.{ext}"
    else:
        filename = f"service_album_{timestamp}_{unique_id}.{ext}"
    
    # Full path
    upload_path = f"services/albums/{filename}"
    
    return upload_path

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=project_image_upload_path, null=True, blank=True, validators=[validate_image])
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    
    # Category fields - Multiple categories allowed
    categories = models.ManyToManyField(
        ProjectCategory, 
        blank=True,
        related_name='projects',
        help_text="Select one or more categories for this project"
    )
    subcategories = models.ManyToManyField(
        ProjectSubcategory, 
        blank=True,
        related_name='projects',
        help_text="Select one or more subcategories (optional)"
    )
    
    # Date fields
    project_date = models.DateField(
        help_text="The date when this project was completed or published",
        verbose_name="Project Date"
    )
    
    # Ordering field - for manual arrangement
    order = models.PositiveIntegerField(
        default=1,
        help_text="Order position for manual arrangement. Lower numbers appear first. Projects are ordered by this field first, then by project_date (newest first)."
    )
    
    def save(self, *args, **kwargs):
        # Set default order to next available position if not set
        if not self.order or self.order == 0:
            max_order = Project.objects.aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        
        # Handle image deletion logic
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
        
        # Auto-optimize image on save
        super().save(*args, **kwargs)
        if self.image:
            optimize_uploaded_image(self.image, self)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', '-project_date']  # Order by manual order first, then by project_date descending

    def get_category_names(self):
        """Get all category names as a list"""
        return [category.name for category in self.categories.all()]

    def get_subcategory_names(self):
        """Get all subcategory names as a list"""
        return [subcategory.name for subcategory in self.subcategories.all()]
    
    def get_primary_category_name(self):
        """Get the first category name for backward compatibility"""
        first_category = self.categories.first()
        return first_category.name if first_category else None

    def get_primary_subcategory_name(self):
        """Get the first subcategory name for backward compatibility"""
        first_subcategory = self.subcategories.first()
        return first_subcategory.name if first_subcategory else None

    def get_category_name(self):
        """Get category name - backward compatibility method"""
        return self.get_primary_category_name()

    def get_subcategory_name(self):
        """Get subcategory name - backward compatibility method"""
        return self.get_primary_subcategory_name()

    def get_album_images_count(self):
        """Get the count of album images for this project"""
        return self.album_images.count()
    
    def get_featured_album_images(self, limit=6):
        """Get album images for preview"""
        if limit is None:
            return self.album_images.all()
        return self.album_images.all()[:limit]
    
    def get_optimized_image_url(self, size='md', format='webp', quality='high'):
        """Get optimized image URL for different sizes and formats"""
        if not self.image:
            return None
        return get_responsive_image_urls(self.image.name, [size])[size]

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to=service_icon_upload_path, null=True, blank=True, validators=[validate_image])
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Service price in USD")
    
    # Category fields - Multiple categories allowed
    categories = models.ManyToManyField(
        ServiceCategory, 
        blank=True,
        related_name='services',
        help_text="Select one or more categories for this service"
    )
    subcategories = models.ManyToManyField(
        ServiceSubcategory, 
        blank=True,
        related_name='services',
        help_text="Select one or more subcategories (optional)"
    )
    
    # Ordering field - for manual arrangement
    order = models.PositiveIntegerField(
        default=1,
        help_text="Order position for manual arrangement. Lower numbers appear first. Services are ordered by this field first, then by name."
    )
    
    def save(self, *args, **kwargs):
        # Set default order to next available position if not set
        if not self.order or self.order == 0:
            max_order = Service.objects.aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        
        # Handle icon deletion logic
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
        
        # Auto-optimize icon on save
        super().save(*args, **kwargs)
        if self.icon:
            optimize_uploaded_image(self.icon, self)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']  # Order by manual order first, then by name

    def get_category_names(self):
        """Get all category names as a list"""
        return [category.name for category in self.categories.all()]

    def get_subcategory_names(self):
        """Get all subcategory names as a list"""
        return [subcategory.name for subcategory in self.subcategories.all()]
    
    def get_primary_category_name(self):
        """Get the first category name for backward compatibility"""
        first_category = self.categories.first()
        return first_category.name if first_category else None

    def get_primary_subcategory_name(self):
        """Get the first subcategory name for backward compatibility"""
        first_subcategory = self.subcategories.first()
        return first_subcategory.name if first_subcategory else None

    def get_category_name(self):
        """Get category name - backward compatibility method"""
        return self.get_primary_category_name()

    def get_subcategory_name(self):
        """Get subcategory name - backward compatibility method"""
        return self.get_primary_subcategory_name()

    def get_album_images_count(self):
        """Get the count of album images for this service"""
        return self.album_images.count()
    
    def get_featured_album_images(self, limit=6):
        """Get album images for preview"""
        if limit is None:
            return self.album_images.all()
        return self.album_images.all()[:limit]
    
    def get_optimized_image_url(self, size='md', format='webp', quality='high'):
        """Get optimized image URL for different sizes and formats"""
        if not self.icon:
            return None
        return get_responsive_image_urls(self.icon.name, [size])[size]


class ProjectImage(models.Model):
    """
    Model for storing multiple images for each project
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='album_images',
        help_text="Project this image belongs to"
    )
    image = models.ImageField(
        upload_to=project_album_image_upload_path, 
        validators=[validate_image],
        help_text="Album image file"
    )
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    title = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Optional title/caption for this image (leave empty for bulk uploads)"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Optional description for this image (leave empty for bulk uploads)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which images should be displayed (0 = first)"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"
    
    def __str__(self):
        if self.title:
            return f"{self.project.title} - {self.title}"
        return f"{self.project.title} - Image {self.pk}"
    
    def save(self, *args, **kwargs):
        # Delete old image if updating and a new image is provided
        if self.pk:
            try:
                old_instance = ProjectImage.objects.get(pk=self.pk)
                # Check if image field has changed and old image exists
                if (old_instance.image and 
                    hasattr(self.image, 'file') and 
                    self.image.file and 
                    old_instance.image.name != self.image.name):
                    # Delete the old image file
                    old_instance.image.delete(save=False)
            except ProjectImage.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the image file when deleting the model instance
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)


class ServiceImage(models.Model):
    """
    Model for storing multiple images for each service
    """
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='album_images',
        help_text="Service this image belongs to"
    )
    image = models.ImageField(
        upload_to=service_album_image_upload_path, 
        validators=[validate_image],
        help_text="Album image file"
    )
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    title = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Optional title/caption for this image (leave empty for bulk uploads)"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Optional description for this image (leave empty for bulk uploads)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which images should be displayed (0 = first)"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = "Service Image"
        verbose_name_plural = "Service Images"
    
    def __str__(self):
        if self.title:
            return f"{self.service.name} - {self.title}"
        return f"{self.service.name} - Image {self.pk}"
    
    def save(self, *args, **kwargs):
        # Delete old image if updating and a new image is provided
        if self.pk:
            try:
                old_instance = ServiceImage.objects.get(pk=self.pk)
                # Check if image field has changed and old image exists
                if (old_instance.image and 
                    hasattr(self.image, 'file') and 
                    self.image.file and 
                    old_instance.image.name != self.image.name):
                    # Delete the old image file
                    old_instance.image.delete(save=False)
            except ServiceImage.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the image file when deleting the model instance
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)


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
