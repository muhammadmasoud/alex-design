from django.db import models
import os
import uuid
import shutil
import logging
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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
        # Check file size (50MB max)
        if image.size > 50 * 1024 * 1024:
            raise ValidationError("Image file too large. Maximum size is 50MB.")
        
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']
        file_extension = os.path.splitext(image.name.lower())[1]
        
        if file_extension not in valid_extensions:
            raise ValidationError(f"Unsupported image format: {file_extension}. Supported formats: JPG, PNG, GIF, BMP, WebP, TIFF")
        
        # Reset file pointer
        image.seek(0)
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error processing image: {str(e)}")

def project_image_upload_path(instance, filename):
    """
    Custom upload path for project main images.
    Creates a project-specific folder structure: media/projects/(project_name)/main_image
    PRODUCTION-SAFE: Handles edge cases and server compatibility
    """
    import uuid
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get file extension
        ext = filename.split('.')[-1].lower()
        
        # Create unique filename with timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if instance.title:
            # Create safe folder name from project title
            project_folder = slugify(instance.title)[:50]  # Limit length
            
            # Ensure folder name is valid for server filesystem
            if not project_folder or project_folder.startswith('.'):
                project_folder = f"project_{timestamp}"
                logger.warning(f"Invalid project title '{instance.title}', using fallback folder name")
        else:
            project_folder = f"project_{timestamp}"
            logger.warning("Project title is empty, using fallback folder name")
        
        filename = f"main_{timestamp}_{unique_id}.{ext}"
        
        # Full path: projects/(project_name)/main_image
        upload_path = f"projects/{project_folder}/{filename}"
        
        return upload_path
        
    except Exception as e:
        logger.error(f"Error generating project upload path: {e}")
        # Fallback to safe path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"main_{timestamp}_{unique_id}.{ext}"
        fallback_path = f"projects/project_{timestamp}_{unique_id}/{filename}"
        return fallback_path

def service_icon_upload_path(instance, filename):
    """
    Custom upload path for service icons.
    Creates a service-specific folder structure: media/services/(service_name)/icon
    PRODUCTION-SAFE: Handles edge cases and server compatibility
    """
    import uuid
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get file extension
        ext = filename.split('.')[-1].lower()
        
        # Create unique filename with timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if instance.name:
            # Create safe folder name from service name
            service_folder = slugify(instance.name)[:50]  # Limit length
            
            # Ensure folder name is valid for server filesystem
            if not service_folder or service_folder.startswith('.'):
                service_folder = f"service_{timestamp}"
                logger.warning(f"Invalid service name '{instance.name}', using fallback folder name")
        else:
            service_folder = f"service_{timestamp}"
            logger.warning("Service name is empty, using fallback folder name")
        
        filename = f"icon_{timestamp}_{unique_id}.{ext}"
        
        # Full path: services/(service_name)/icon
        upload_path = f"services/{service_folder}/{filename}"
        
        return upload_path
        
    except Exception as e:
        logger.error(f"Error generating service upload path: {e}")
        # Fallback to safe path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"icon_{timestamp}_{unique_id}.{ext}"
        fallback_path = f"services/service_{timestamp}_{unique_id}/{filename}"
        return fallback_path

def project_album_image_upload_path(instance, filename):
    """
    Custom upload path for project album images.
    Creates a project-specific folder structure: media/projects/(project_name)/album/
    PRODUCTION-SAFE: Handles edge cases and server compatibility
    """
    import uuid
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get file extension
        ext = filename.split('.')[-1].lower()
        
        # Create unique filename with timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if instance.project and instance.project.title:
            # Create safe folder name from project title
            project_folder = slugify(instance.project.title)[:50]  # Limit length
            
            # Ensure folder name is valid for server filesystem
            if not project_folder or project_folder.startswith('.'):
                project_folder = f"project_{timestamp}"
                logger.warning(f"Invalid project title '{instance.project.title}', using fallback folder name")
        else:
            project_folder = f"project_{timestamp}"
            logger.warning("Project or project title is missing, using fallback folder name")
        
        filename = f"album_{timestamp}_{unique_id}.{ext}"
        
        # Full path: projects/(project_name)/album/album_image
        upload_path = f"projects/{project_folder}/album/{filename}"
        
        return upload_path
        
    except Exception as e:
        logger.error(f"Error generating project album upload path: {e}")
        # Fallback to safe path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"album_{timestamp}_{unique_id}.{ext}"
        fallback_path = f"projects/project_{timestamp}_{unique_id}/album/{filename}"
        return fallback_path

def service_album_image_upload_path(instance, filename):
    """
    Custom upload path for service album images.
    Creates a service-specific folder structure: media/services/(service_name)/album/
    PRODUCTION-SAFE: Handles edge cases and server compatibility
    """
    import uuid
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get file extension
        ext = filename.split('.')[-1].lower()
        
        # Create unique filename with timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if instance.service and instance.service.name:
            # Create safe folder name from service name
            service_folder = slugify(instance.service.name)[:50]  # Limit length
            
            # Ensure folder name is valid for server filesystem
            if not service_folder or service_folder.startswith('.'):
                service_folder = f"service_{timestamp}"
                logger.warning(f"Invalid service name '{instance.service.name}', using fallback folder name")
        else:
            service_folder = f"service_{timestamp}"
            logger.warning("Service or service name is missing, using fallback folder name")
        
        filename = f"album_{timestamp}_{unique_id}.{ext}"
        
        # Full path: services/(service_name)/album/album_image
        upload_path = f"services/{service_folder}/album/{filename}"
        
        return upload_path
        
    except Exception as e:
        logger.error(f"Error generating service album upload path: {e}")
        # Fallback to safe path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"album_{timestamp}_{unique_id}.{ext}"
        fallback_path = f"services/service_{timestamp}_{unique_id}/album/{filename}"
        return fallback_path

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=project_image_upload_path, null=True, blank=True, validators=[validate_image])
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    
    # Original file path - store the original unoptimized file path
    original_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the original unoptimized file")
    
    # Optimized image paths - store the .webp paths instead of original
    optimized_image = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the optimized .webp version of the main image")
    optimized_image_small = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the small optimized .webp version")
    optimized_image_medium = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the medium optimized .webp version")
    optimized_image_large = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the large optimized .webp version")
    
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
        # Check if we're only updating optimized fields (skip cleanup logic)
        update_fields = kwargs.get('update_fields', [])
        if update_fields and all(field.startswith('optimized_') or field == 'original_file_path' for field in update_fields):
            # Only updating optimized fields, skip cleanup logic
            super().save(*args, **kwargs)
            return
        
        # Set default order to next available position if not set
        if not self.order or self.order == 0:
            # Use a more efficient approach to avoid aggregate on every save
            try:
                # Get the last project by order (most efficient query)
                last_project = Project.objects.only('order').order_by('-order').first()
                self.order = (last_project.order if last_project else 0) + 1
            except:
                # Fallback to aggregate if the above fails
                max_order = Project.objects.aggregate(models.Max('order'))['order__max']
                self.order = (max_order or 0) + 1
        
        # Handle title change and file reorganization
        if self.pk:
            try:
                old_instance = Project.objects.get(pk=self.pk)
                
                # Check if title has changed
                if old_instance.title != self.title:
                    # Move files to new folder structure
                    self._move_files_to_new_folder(old_instance.title, self.title)
                
                # Handle image deletion logic - delete old image and optimized versions
                if old_instance.image:
                    # Check if image has changed (different scenarios)
                    image_changed = False
                    change_reason = ""
                    
                    if not self.image:
                        # Image was removed
                        image_changed = True
                        change_reason = "image_removed"
                    elif hasattr(self.image, 'name') and old_instance.image.name != self.image.name:
                        # Image file name changed (new upload)
                        image_changed = True
                        change_reason = f"name_changed: {old_instance.image.name} -> {self.image.name}"
                    elif hasattr(self.image, '_file') and self.image._file:
                        # New image file uploaded (Django admin scenario)
                        image_changed = True
                        change_reason = "new_file_uploaded_admin"
                    elif hasattr(self.image, 'file'):
                        # Another way new image can be detected - handle missing files gracefully
                        try:
                            if self.image.file:
                                image_changed = True
                                change_reason = "new_file_uploaded_api"
                        except (FileNotFoundError, ValueError):
                            # File doesn't exist, no need to check
                            pass
                    
                    if image_changed:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Project {self.title}: Will clean up old image asynchronously: {change_reason}")
                        
                        # Store old image path for async cleanup
                        old_image_path = old_instance.image.name if old_instance.image else None
                        
                        # Clear the current instance's optimized paths so they get regenerated
                        self.optimized_image = None
                        self.optimized_image_small = None
                        self.optimized_image_medium = None
                        self.optimized_image_large = None
                        
                        # Queue async cleanup after save completes
                        if old_image_path:
                            from django.db import transaction
                            def queue_cleanup():
                                try:
                                    from .async_optimizer import AsyncImageOptimizer
                                    # We'll add a cleanup method to AsyncImageOptimizer
                                    AsyncImageOptimizer.queue_file_cleanup('project', self.id, old_image_path)
                                except Exception as e:
                                    logger.error(f"Failed to queue cleanup for {old_image_path}: {e}")
                            
                            transaction.on_commit(queue_cleanup)
                        
                        logger.info(f"Project {self.title}: Queued async cleanup for old image")
                    else:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Project {self.title}: No image change detected")
            except Project.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    def _move_files_to_new_folder(self, old_title, new_title):
        """
        Move project files from old folder to new folder when title changes
        PRODUCTION-SAFE: Uses atomic operations and proper error handling
        """
        import os
        import shutil
        import logging
        from django.conf import settings
        from django.core.exceptions import ValidationError
        from .image_optimizer import ImageOptimizer
        
        # Set up logging
        logger = logging.getLogger(__name__)
        
        old_folder = slugify(old_title)[:50]
        new_folder = slugify(new_title)[:50]
        
        # Validate folder names for server compatibility
        if not old_folder or not new_folder:
            logger.warning(f"Invalid folder names: old='{old_folder}', new='{new_folder}'")
            return
        
        old_path = os.path.join(settings.MEDIA_ROOT, 'projects', old_folder)
        new_path = os.path.join(settings.MEDIA_ROOT, 'projects', new_folder)
        
        # Only move if old folder exists and is different from new folder
        if os.path.exists(old_path) and old_folder != new_folder:
            try:
                # Create new folder with proper permissions
                os.makedirs(new_path, mode=0o755, exist_ok=True)
                
                # Use atomic move operation for better safety
                temp_path = f"{new_path}_temp_{os.getpid()}"
                
                # First move to temporary location
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                
                shutil.move(old_path, temp_path)
                
                # Then move to final location (atomic)
                shutil.move(temp_path, new_path)
                
                logger.info(f"Successfully moved project files from '{old_folder}' to '{new_folder}'")
                
            except OSError as e:
                # Handle OS-level errors (permissions, disk space, etc.)
                logger.error(f"OS Error moving files from {old_path} to {new_path}: {e}")
                
                # Try to restore old folder if move failed
                try:
                    if os.path.exists(temp_path) and not os.path.exists(old_path):
                        shutil.move(temp_path, old_path)
                        logger.info(f"Restored old folder '{old_path}' after failed move")
                except Exception as restore_error:
                    logger.error(f"Failed to restore old folder: {restore_error}")
                    
            except Exception as e:
                # Handle other unexpected errors
                logger.error(f"Unexpected error moving files from {old_path} to {new_path}: {e}")
                
                # Try to restore old folder
                try:
                    if os.path.exists(temp_path) and not os.path.exists(old_path):
                        shutil.move(temp_path, old_path)
                        logger.info(f"Restored old folder '{old_path}' after unexpected error")
                except Exception as restore_error:
                    logger.error(f"Failed to restore old folder: {restore_error}")
                    
            finally:
                # Clean up any temporary paths
                try:
                    if os.path.exists(temp_path):
                        shutil.rmtree(temp_path)
                except Exception:
                    pass

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', '-project_date']
        indexes = [
            models.Index(fields=['order', '-project_date']),
            models.Index(fields=['project_date']),
            models.Index(fields=['order']),
        ]  # Order by manual order first, then by project_date descending

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
    
    def get_optimized_image_url(self, size='medium', format='webp'):
        """
        Get the URL for the optimized main image
        Returns the path to the optimized version if it exists
        """
        if not self.image:
            return None
        
        from .image_optimizer import ImageOptimizer
        return ImageOptimizer.get_optimized_image_url(self.image.path, size, format)
    
    def get_optimized_album_image_urls(self, size='medium', format='webp'):
        """
        Get optimized URLs for all album images
        Returns a list of optimized image URLs
        """
        from .image_optimizer import ImageOptimizer
        optimized_urls = []
        
        for album_image in self.album_images.all():
            if album_image.image:
                optimized_url = ImageOptimizer.get_optimized_image_url(album_image.image.path, size, format)
                optimized_urls.append(optimized_url)
        
        return optimized_urls

    def get_display_image_url(self, size='medium', format='webp'):
        """Get the optimized image URL for display - automatically uses optimized version"""
        if not self.image:
            return None
        from .image_optimizer import ImageOptimizer
        optimized_url = ImageOptimizer.get_optimized_image_url(self.image.path, size, format)
        if optimized_url:
            return optimized_url
        return self.image.url  # Fallback to original if optimization failed

    def get_display_album_urls(self, size='medium', format='webp'):
        """Get optimized album image URLs for display - automatically uses optimized versions"""
        from .image_optimizer import ImageOptimizer
        optimized_urls = []
        for album_image in self.album_images.all():
            if album_image.image:
                optimized_url = ImageOptimizer.get_optimized_image_url(album_image.image.path, size, format)
                if optimized_url:
                    optimized_urls.append(optimized_url)
                else:
                    optimized_urls.append(album_image.image.url)  # Fallback to original
        return optimized_urls

    def optimize_images_manually(self):
        """
        Manually trigger image optimization for this project
        Useful if automatic optimization fails
        """
        try:
            from .image_optimizer import ImageOptimizer
            ImageOptimizer.optimize_project_images(self)
            return True, "Images optimized successfully"
        except Exception as e:
            return False, f"Optimization failed: {str(e)}"

    def delete(self, *args, **kwargs):
        """
        Custom delete method to ensure complete cleanup of project and all related files
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Store project info before deletion for logging
            project_title = self.title
            project_id = self.pk
            
            logger.info(f"Starting deletion process for project: {project_title} (ID: {project_id})")
            
            # 1. Delete the main project image and its optimized versions
            if self.image:
                try:
                    from .image_optimizer import ImageOptimizer
                    ImageOptimizer.delete_image_file(self.image)
                    logger.info(f"Deleted main project image for: {project_title}")
                except Exception as e:
                    logger.error(f"Error deleting main project image for {project_title}: {str(e)}")
            
            # 2. Delete all project album images (this should cascade automatically via foreign key)
            album_images_count = self.album_images.count()
            if album_images_count > 0:
                logger.info(f"Found {album_images_count} album images for project: {project_title}")
                # The album images will be deleted automatically due to CASCADE foreign key
                # and their signals will handle file cleanup
            
            # 3. Delete the entire project folder using ImageOptimizer
            try:
                # Longer delay to allow file handles to close, especially for optimized images
                import time
                import gc
                gc.collect()
                time.sleep(1.0)
                gc.collect()
                time.sleep(1.0)
                
                from .image_optimizer import ImageOptimizer
                folder_deleted = ImageOptimizer.delete_project_folder(self)
                if folder_deleted:
                    logger.info(f"Successfully deleted project folder for: {project_title}")
                else:
                    logger.warning(f"Project folder deletion returned False for: {project_title}")
            except Exception as e:
                logger.error(f"Error deleting project folder for {project_title}: {str(e)}")
                
                # Fallback: Try to delete folder manually
                try:
                    from django.conf import settings
                    project_folder_name = slugify(project_title)[:50]
                    if project_folder_name:
                        project_folder_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder_name)
                        if os.path.exists(project_folder_path):
                            shutil.rmtree(project_folder_path)
                            logger.info(f"Fallback deletion successful for project folder: {project_folder_path}")
                        else:
                            logger.info(f"Project folder not found during fallback: {project_folder_path}")
                except Exception as fallback_error:
                    logger.error(f"Fallback folder deletion also failed for {project_title}: {str(fallback_error)}")
            
            # 4. Perform the actual model deletion
            super().delete(*args, **kwargs)
            logger.info(f"Successfully completed deletion of project: {project_title} (ID: {project_id})")
            
        except Exception as e:
            logger.error(f"Critical error during project deletion for {project_title}: {str(e)}")
            # Still attempt to delete the model to avoid leaving orphaned records
            try:
                super().delete(*args, **kwargs)
                logger.info(f"Model deletion succeeded despite cleanup errors for: {project_title}")
            except Exception as model_delete_error:
                logger.error(f"Model deletion also failed for {project_title}: {str(model_delete_error)}")
                raise model_delete_error


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to=service_icon_upload_path, null=True, blank=True, validators=[validate_image])
    original_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Original filename when uploaded")
    
    # Original file path - store the original unoptimized file path
    original_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the original unoptimized file")
    
    # Optimized icon paths - store the .webp paths instead of original
    optimized_icon = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the optimized .webp version of the icon")
    optimized_icon_small = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the small optimized .webp version")
    optimized_icon_medium = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the medium optimized .webp version")
    optimized_icon_large = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the large optimized .webp version")
    
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
        # Check if we're only updating optimized fields (skip cleanup logic)
        update_fields = kwargs.get('update_fields', [])
        if update_fields and all(field.startswith('optimized_') or field == 'original_file_path' for field in update_fields):
            # Only updating optimized fields, skip cleanup logic
            super().save(*args, **kwargs)
            return
        
        # Set default order to next available position if not set
        if not self.order or self.order == 0:
            # Use a more efficient approach to avoid aggregate on every save
            try:
                # Get the last service by order (most efficient query)
                last_service = Service.objects.only('order').order_by('-order').first()
                self.order = (last_service.order if last_service else 0) + 1
            except:
                # Fallback to aggregate if the above fails
                max_order = Service.objects.aggregate(models.Max('order'))['order__max']
                self.order = (max_order or 0) + 1
        
        # Handle name change and file reorganization
        if self.pk:
            try:
                old_instance = Service.objects.get(pk=self.pk)
                
                # Check if name has changed
                if old_instance.name != self.name:
                    # Move files to new folder structure
                    self._move_files_to_new_folder(old_instance.name, self.name)
                
                # Handle icon deletion logic - delete old icon and optimized versions
                if old_instance.icon:
                    # Check if icon has changed (different scenarios)
                    icon_changed = False
                    
                    # Safely check for icon changes
                    try:
                        if not self.icon:
                            # Icon was removed
                            icon_changed = True
                        elif hasattr(self.icon, 'name') and old_instance.icon.name != self.icon.name:
                            # Icon file name changed (new upload)
                            icon_changed = True
                        elif hasattr(self.icon, '_file') and self.icon._file:
                            # New icon file uploaded (Django admin scenario)
                            icon_changed = True
                        elif hasattr(self.icon, 'file'):
                            # Another way new icon can be detected - handle missing files gracefully
                            try:
                                if self.icon.file:
                                    icon_changed = True
                            except (FileNotFoundError, ValueError, OSError):
                                # File doesn't exist, no need to check
                                pass
                    except (FileNotFoundError, ValueError, OSError) as e:
                        # Handle any file-related errors gracefully
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Service {self.name}: File error during save check: {e}")
                        pass
                    
                    if icon_changed:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Service {self.name}: Will clean up old icon asynchronously")
                        
                        # Store old icon path for async cleanup
                        old_icon_path = old_instance.icon.name if old_instance.icon else None
                        
                        # Clear the current instance's optimized paths so they get regenerated
                        self.optimized_icon = None
                        self.optimized_icon_small = None
                        self.optimized_icon_medium = None
                        self.optimized_icon_large = None
                        
                        # Queue async cleanup after save completes
                        if old_icon_path:
                            from django.db import transaction
                            def queue_cleanup():
                                try:
                                    from .async_optimizer import AsyncImageOptimizer
                                    AsyncImageOptimizer.queue_file_cleanup('service', self.id, old_icon_path)
                                except Exception as e:
                                    logger.error(f"Failed to queue cleanup for {old_icon_path}: {e}")
                            
                            transaction.on_commit(queue_cleanup)
                        
                        logger.info(f"Service {self.name}: Queued async cleanup for old icon")
            except Service.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    def _move_files_to_new_folder(self, old_name, new_name):
        """
        Move service files from old folder to new folder when name changes
        PRODUCTION-SAFE: Uses atomic operations and proper error handling
        """
        import os
        import shutil
        import logging
        from django.conf import settings
        from django.core.exceptions import ValidationError
        
        # Set up logging
        logger = logging.getLogger(__name__)
        
        old_folder = slugify(old_name)[:50]
        new_folder = slugify(new_name)[:50]
        
        # Validate folder names for server compatibility
        if not old_folder or not new_folder:
            logger.warning(f"Invalid folder names: old='{old_folder}', new='{new_folder}'")
            return
        
        old_path = os.path.join(settings.MEDIA_ROOT, 'services', old_folder)
        new_path = os.path.join(settings.MEDIA_ROOT, 'services', new_folder)
        
        # Only move if old folder exists and is different from new folder
        if os.path.exists(old_path) and old_folder != new_folder:
            try:
                # Create new folder with proper permissions
                os.makedirs(new_path, mode=0o755, exist_ok=True)
                
                # Use atomic move operation for better safety
                temp_path = f"{new_path}_temp_{os.getpid()}"
                
                # First move to temporary location
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                
                shutil.move(old_path, temp_path)
                
                # Then move to final location (atomic)
                shutil.move(temp_path, new_path)
                
                logger.info(f"Successfully moved service files from '{old_folder}' to '{new_folder}'")
                
            except OSError as e:
                # Handle OS-level errors (permissions, disk space, etc.)
                logger.error(f"OS Error moving files from {old_path} to {new_path}: {e}")
                
                # Try to restore old folder if move failed
                try:
                    if os.path.exists(temp_path) and not os.path.exists(old_path):
                        shutil.move(temp_path, old_path)
                        logger.info(f"Restored old folder '{old_path}' after failed move")
                except Exception as restore_error:
                    logger.error(f"Failed to restore old folder: {restore_error}")
                    
            except Exception as e:
                # Handle other unexpected errors
                logger.error(f"Unexpected error moving files from {old_path} to {new_path}: {e}")
                
                # Try to restore old folder
                try:
                    if os.path.exists(temp_path) and not os.path.exists(old_path):
                        shutil.move(temp_path, old_path)
                        logger.info(f"Restored old folder '{old_path}' after unexpected error")
                except Exception as restore_error:
                    logger.error(f"Failed to restore old folder: {restore_error}")
                    
            finally:
                # Clean up any temporary paths
                try:
                    if os.path.exists(temp_path):
                        shutil.rmtree(temp_path)
                except Exception:
                    pass

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
    
    def get_optimized_icon_url(self, size='medium', format='webp'):
        """
        Get the URL for the optimized service icon
        Returns the path to the optimized version if it exists
        """
        if not self.icon:
            return None
        
        from .image_optimizer import ImageOptimizer
        return ImageOptimizer.get_optimized_image_url(self.icon.path, size, format)
    
    def get_optimized_album_image_urls(self, size='medium', format='webp'):
        """
        Get optimized URLs for all album images
        Returns a list of optimized image URLs
        """
        from .image_optimizer import ImageOptimizer
        optimized_urls = []
        
        for album_image in self.album_images.all():
            if album_image.image:
                optimized_url = ImageOptimizer.get_optimized_image_url(album_image.image.path, size, format)
                optimized_urls.append(optimized_url)
        
        return optimized_urls

    def get_display_icon_url(self, size='medium', format='webp'):
        """Get the optimized icon URL for display - automatically uses optimized version"""
        if not self.icon:
            return None
        from .image_optimizer import ImageOptimizer
        optimized_url = ImageOptimizer.get_optimized_image_url(self.icon.path, size, format)
        if optimized_url:
            return optimized_url
        return self.icon.url  # Fallback to original if optimization failed

    def get_display_album_urls(self, size='medium', format='webp'):
        """Get optimized album image URLs for display - automatically uses optimized versions"""
        from .image_optimizer import ImageOptimizer
        optimized_urls = []
        for album_image in self.album_images.all():
            if album_image.image:
                optimized_url = ImageOptimizer.get_optimized_image_url(album_image.image.path, size, format)
                if optimized_url:
                    optimized_urls.append(optimized_url)
                else:
                    optimized_urls.append(album_image.image.url)  # Fallback to original
        return optimized_urls

    def optimize_images_manually(self):
        """
        Manually trigger image optimization for this service
        Useful if automatic optimization fails
        """
        try:
            from .image_optimizer import ImageOptimizer
            ImageOptimizer.optimize_service_images(self)
            return True, "Images optimized successfully"
        except Exception as e:
            return False, f"Optimization failed: {str(e)}"

    def delete(self, *args, **kwargs):
        """
        Custom delete method to ensure complete cleanup of service and all related files
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Store service info before deletion for logging
            service_name = self.name
            service_id = self.pk
            
            logger.info(f"Starting deletion process for service: {service_name} (ID: {service_id})")
            
            # 1. Delete the service icon and its optimized versions
            if self.icon:
                try:
                    from .image_optimizer import ImageOptimizer
                    ImageOptimizer.delete_image_file(self.icon)
                    logger.info(f"Deleted service icon for: {service_name}")
                except Exception as e:
                    logger.error(f"Error deleting service icon for {service_name}: {str(e)}")
            
            # 2. Delete all service album images (this should cascade automatically via foreign key)
            album_images_count = self.album_images.count()
            if album_images_count > 0:
                logger.info(f"Found {album_images_count} album images for service: {service_name}")
                # The album images will be deleted automatically due to CASCADE foreign key
                # and their signals will handle file cleanup
            
            # 3. Delete the entire service folder using ImageOptimizer
            try:
                from .image_optimizer import ImageOptimizer
                folder_deleted = ImageOptimizer.delete_service_folder(self)
                if folder_deleted:
                    logger.info(f"Successfully deleted service folder for: {service_name}")
                else:
                    logger.warning(f"Service folder deletion returned False for: {service_name}")
            except Exception as e:
                logger.error(f"Error deleting service folder for {service_name}: {str(e)}")
                
                # Fallback: Try to delete folder manually
                try:
                    from django.conf import settings
                    service_folder_name = slugify(service_name)[:50]
                    if service_folder_name:
                        service_folder_path = os.path.join(settings.MEDIA_ROOT, 'services', service_folder_name)
                        if os.path.exists(service_folder_path):
                            shutil.rmtree(service_folder_path)
                            logger.info(f"Fallback deletion successful for service folder: {service_folder_path}")
                        else:
                            logger.info(f"Service folder not found during fallback: {service_folder_path}")
                except Exception as fallback_error:
                    logger.error(f"Fallback folder deletion also failed for {service_name}: {str(fallback_error)}")
            
            # 4. Perform the actual model deletion
            super().delete(*args, **kwargs)
            logger.info(f"Successfully completed deletion of service: {service_name} (ID: {service_id})")
            
        except Exception as e:
            logger.error(f"Critical error during service deletion for {service_name}: {str(e)}")
            # Still attempt to delete the model to avoid leaving orphaned records
            try:
                super().delete(*args, **kwargs)
                logger.info(f"Model deletion succeeded despite cleanup errors for: {service_name}")
            except Exception as model_delete_error:
                logger.error(f"Model deletion also failed for {service_name}: {str(model_delete_error)}")
                raise model_delete_error


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
    
    # Original file path - store the original unoptimized file path
    original_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the original unoptimized file")
    
    # Optimized image paths - store the .webp paths instead of original
    optimized_image = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the optimized .webp version of the album image")
    optimized_image_small = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the small optimized .webp version")
    optimized_image_medium = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the medium optimized .webp version")
    optimized_image_large = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the large optimized .webp version")
    
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
        # Check if we're only updating optimized fields (skip cleanup logic)
        update_fields = kwargs.get('update_fields', [])
        if update_fields and all(field.startswith('optimized_') or field == 'original_file_path' for field in update_fields):
            # Only updating optimized fields, skip cleanup logic
            super().save(*args, **kwargs)
            return
        
        # Delete old image if updating and a new image is provided
        if self.pk:
            try:
                old_instance = ProjectImage.objects.get(pk=self.pk)
                # Check if image field has changed and old image exists
                if old_instance.image:
                    # Check if image has changed (different scenarios)
                    image_changed = False
                    
                    if not self.image:
                        # Image was removed
                        image_changed = True
                    elif hasattr(self.image, 'name') and old_instance.image.name != self.image.name:
                        # Image file name changed (new upload)
                        image_changed = True
                    elif hasattr(self.image, '_file') and self.image._file:
                        # New image file uploaded (Django admin scenario)
                        image_changed = True
                    elif hasattr(self.image, 'file') and self.image.file:
                        # Another way new image can be detected
                        image_changed = True
                    
                    if image_changed:
                        # Delete the old image file AND its optimized versions
                        from .image_optimizer import ImageOptimizer
                        ImageOptimizer.delete_image_file(old_instance.image)
                        
                        # Also clear the optimized path fields for the old image
                        old_instance.optimized_image = None
                        old_instance.optimized_image_small = None
                        old_instance.optimized_image_medium = None
                        old_instance.optimized_image_large = None
                        
                        # Clear the current instance's optimized paths so they get regenerated
                        self.optimized_image = None
                        self.optimized_image_small = None
                        self.optimized_image_medium = None
                        self.optimized_image_large = None
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
    
    # Original file path - store the original unoptimized file path
    original_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the original unoptimized file")
    
    # Optimized image paths - store the .webp paths instead of original
    optimized_image = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the optimized .webp version of the album image")
    optimized_image_small = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the small optimized .webp version")
    optimized_image_medium = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the medium optimized .webp version")
    optimized_image_large = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the large optimized .webp version")
    
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
        # Check if we're only updating optimized fields (skip cleanup logic)
        update_fields = kwargs.get('update_fields', [])
        if update_fields and all(field.startswith('optimized_') or field == 'original_file_path' for field in update_fields):
            # Only updating optimized fields, skip cleanup logic
            super().save(*args, **kwargs)
            return
        
        # Delete old image if updating and a new image is provided
        if self.pk:
            try:
                old_instance = ServiceImage.objects.get(pk=self.pk)
                # Check if image field has changed and old image exists
                if old_instance.image:
                    # Check if image has changed (different scenarios)
                    image_changed = False
                    
                    if not self.image:
                        # Image was removed
                        image_changed = True
                    elif hasattr(self.image, 'name') and old_instance.image.name != self.image.name:
                        # Image file name changed (new upload)
                        image_changed = True
                    elif hasattr(self.image, '_file') and self.image._file:
                        # New image file uploaded (Django admin scenario)
                        image_changed = True
                    elif hasattr(self.image, 'file') and self.image.file:
                        # Another way new image can be detected
                        image_changed = True
                    
                    if image_changed:
                        # Delete the old image file AND its optimized versions
                        from .image_optimizer import ImageOptimizer
                        ImageOptimizer.delete_image_file(old_instance.image)
                        
                        # Also clear the optimized path fields for the old image
                        old_instance.optimized_image = None
                        old_instance.optimized_image_small = None
                        old_instance.optimized_image_medium = None
                        old_instance.optimized_image_large = None
                        
                        # Clear the current instance's optimized paths so they get regenerated
                        self.optimized_image = None
                        self.optimized_image_small = None
                        self.optimized_image_medium = None
                        self.optimized_image_large = None
            except ServiceImage.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the image file and all its optimized versions when deleting the model instance
        if self.image:
            try:
                from .image_optimizer import ImageOptimizer
                ImageOptimizer.delete_image_file(self.image)
            except Exception as e:
                # Fallback to basic deletion if ImageOptimizer fails
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


# Consultation Booking Models
class ConsultationSettings(models.Model):
    """
    Model for storing consultation settings like meeting duration and working hours
    """
    # Meeting configuration
    meeting_duration_minutes = models.PositiveIntegerField(
        default=45,
        help_text="Duration of each consultation meeting in minutes"
    )
    buffer_time_minutes = models.PositiveIntegerField(
        default=15,
        help_text="Buffer time between meetings in minutes"
    )
    
    # Working hours for each day (stored as time strings: "09:00-17:00" or empty for day off)
    monday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Monday (e.g., '09:00-17:00') or leave empty for day off"
    )
    tuesday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Tuesday (e.g., '09:00-17:00') or leave empty for day off"
    )
    wednesday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Wednesday (e.g., '09:00-17:00') or leave empty for day off"
    )
    thursday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Thursday (e.g., '09:00-17:00') or leave empty for day off"
    )
    friday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Friday (e.g., '09:00-17:00') or leave empty for day off"
    )
    saturday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Saturday (e.g., '09:00-17:00') or leave empty for day off"
    )
    sunday_hours = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Working hours for Sunday (e.g., '09:00-17:00') or leave empty for day off"
    )
    
    # Other settings
    booking_enabled = models.BooleanField(
        default=True,
        help_text="Enable or disable consultation bookings globally"
    )
    advance_booking_days = models.PositiveIntegerField(
        default=30,
        help_text="How many days in advance clients can book consultations"
    )
    minimum_notice_hours = models.PositiveIntegerField(
        default=24,
        help_text="Minimum hours notice required for booking a consultation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consultation Settings"
        verbose_name_plural = "Consultation Settings"
    
    def __str__(self):
        return f"Consultation Settings (Duration: {self.meeting_duration_minutes}min)"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and ConsultationSettings.objects.exists():
            # Update existing instance instead of creating new one
            existing = ConsultationSettings.objects.first()
            for field in self._meta.fields:
                if field.name not in ['id', 'created_at']:
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return existing
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the consultation settings instance (creates default if none exists)"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'meeting_duration_minutes': 45,
                'buffer_time_minutes': 15,
                'monday_hours': '09:00-17:00',
                'tuesday_hours': '09:00-17:00',
                'wednesday_hours': '09:00-17:00',
                'thursday_hours': '09:00-17:00',
                'friday_hours': '09:00-17:00',
                'saturday_hours': '',
                'sunday_hours': '',
                'booking_enabled': True,
                'advance_booking_days': 30,
                'minimum_notice_hours': 24,
            }
        )
        return settings
    
    def get_working_hours_for_day(self, weekday):
        """Get working hours for a specific weekday (0=Monday, 6=Sunday)"""
        day_fields = [
            'monday_hours', 'tuesday_hours', 'wednesday_hours', 
            'thursday_hours', 'friday_hours', 'saturday_hours', 'sunday_hours'
        ]
        if 0 <= weekday <= 6:
            return getattr(self, day_fields[weekday]) or ''
        return ''
    
    def is_working_day(self, weekday):
        """Check if a specific weekday is a working day"""
        hours = self.get_working_hours_for_day(weekday)
        return bool(hours and hours.strip())


class DayOff(models.Model):
    """
    Model for storing specific days that are blocked for consultations
    """
    date = models.DateField(
        unique=True,
        help_text="Date to block for consultations"
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional reason for the day off (e.g., 'Holiday', 'Personal')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Day Off"
        verbose_name_plural = "Days Off"
        ordering = ['date']
    
    def __str__(self):
        reason_text = f" ({self.reason})" if self.reason else ""
        return f"Day Off: {self.date}{reason_text}"


class Booking(models.Model):
    """
    Model for storing consultation bookings
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    # Client information
    client_name = models.CharField(
        max_length=100,
        help_text="Full name of the client"
    )
    client_email = models.EmailField(
        help_text="Email address of the client"
    )
    client_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number of the client (optional)"
    )
    
    # Booking details
    date = models.DateField(
        help_text="Date of the consultation"
    )
    time = models.TimeField(
        help_text="Start time of the consultation"
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Duration of the consultation in minutes"
    )
    
    # Additional information
    project_details = models.TextField(
        blank=True,
        null=True,
        help_text="Details about the client's project or consultation needs"
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Additional message from the client"
    )
    
    # Status and admin notes
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for admin use"
    )
    cancellation_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason provided when cancelling the consultation"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consultation Booking"
        verbose_name_plural = "Consultation Bookings"
        ordering = ['-date', '-time']
        unique_together = ['date', 'time']  # Prevent double booking same time slot
        indexes = [
            models.Index(fields=['date', 'time']),
            models.Index(fields=['status']),
            models.Index(fields=['client_email']),
        ]
    
    def __str__(self):
        return f"{self.client_name} - {self.date} {self.time} ({self.status})"
    
    def get_end_time(self):
        """Calculate the end time of the consultation"""
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.time()
    
    def is_past(self):
        """Check if the consultation date is in the past"""
        from datetime import date
        return self.date < date.today()
    
    @classmethod
    def has_monthly_booking(cls, client_email, target_date):
        """Check if client already has a booking in the same month"""
        from datetime import date, timedelta
        
        # Get the first and last day of the target month
        first_day = target_date.replace(day=1)
        if target_date.month == 12:
            last_day = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        
        # Check for existing bookings in that month (excluding cancelled ones)
        existing_bookings = cls.objects.filter(
            client_email=client_email,
            date__gte=first_day,
            date__lte=last_day,
            status__in=['pending', 'confirmed', 'completed']  # Exclude cancelled and no_show
        )
        
        return existing_bookings.exists()
    
    def get_datetime_range(self):
        """Get the full datetime range of the consultation"""
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return start_datetime, end_datetime
    
    def is_past(self):
        """Check if the consultation is in the past"""
        from datetime import datetime
        consultation_datetime = datetime.combine(self.date, self.time)
        return consultation_datetime < datetime.now()
    
    def can_be_cancelled(self):
        """Check if the booking can still be cancelled (not in the past and not already cancelled/completed)"""
        return not self.is_past() and self.status not in ['cancelled', 'completed', 'no_show']
