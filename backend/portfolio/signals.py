"""
Signals for Alex Design Portfolio
Handles automatic operations when models are created, updated, or deleted
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
import os
import logging
import shutil
import threading
from .models import Project, Service, ProjectImage, ServiceImage
from .image_optimizer import ImageOptimizer
from .async_optimizer import AsyncImageOptimizer

logger = logging.getLogger(__name__)

# Thread lock to prevent duplicate optimizations (legacy, but kept for safety)
optimization_lock = threading.Lock()
currently_optimizing = set()

@receiver(post_save, sender=Project)
def optimize_project_images_on_save(sender, instance, created, **kwargs):
    """
    Automatically optimize project images when a project is created or updated
    OPTIMIZED: Uses async queue system to prevent blocking HTTP responses
    """
    try:
        # Skip optimization entirely if this is just a text-only update
        # Check if this save was triggered by updating optimized image fields (avoid infinite loop)
        update_fields = kwargs.get('update_fields')
        if update_fields and all(field.startswith('optimized_') for field in update_fields):
            logger.debug(f"Skipping optimization - optimized fields update for project: {instance.title}")
            return
        
        # Fast path: For existing projects, only optimize if new images were uploaded
        if not created:
            # Check if any image files were actually changed in this update
            image_changed = False
            
            # Check if this is an API update with new files
            if hasattr(instance, '_image_files_changed') and instance._image_files_changed:
                image_changed = True
                logger.info(f"Project has new image files - will optimize: {instance.title}")
            else:
                # For existing projects without new files, skip optimization entirely
                logger.info(f"FAST PATH: Skipping optimization - no new image files for existing project: {instance.title}")
                return
        else:
            # For new projects, check if they have images to optimize
            has_main_image = bool(instance.image)
            if not has_main_image:
                # Album images will be handled by ProjectImage signals
                logger.debug(f"New project created without main image - skipping optimization: {instance.title}")
                return
            
            logger.info(f"New project created with main image - queuing optimization: {instance.title}")
        
        # Queue optimization asynchronously - this is instantaneous and non-blocking
        AsyncImageOptimizer.queue_project_optimization(
            project_id=instance.id,
            operation_type='create' if created else 'update'
        )
        
        # Clear cache since we're processing image optimization
        cache_key = f"project_{instance.id}_images"
        cache.delete(cache_key)
        
    except Exception as e:
        logger.error(f"Error in project image optimization signal: {str(e)}")

@receiver(post_save, sender=Service)
def optimize_service_images_on_save(sender, instance, created, **kwargs):
    """
    Automatically optimize service images when a service is created or updated
    OPTIMIZED: Uses async queue system to prevent blocking HTTP responses
    """
    try:
        # Skip optimization entirely if this is just a text-only update
        # Check if this save was triggered by updating optimized image fields (avoid infinite loop)
        update_fields = kwargs.get('update_fields')
        if update_fields and all(field.startswith('optimized_') for field in update_fields):
            logger.debug(f"Skipping optimization - optimized fields update for service: {instance.name}")
            return
        
        # Fast path: For existing services, only optimize if new images were uploaded
        if not created:
            # Check if any image files were actually changed in this update
            image_changed = False
            
            # Check if this is an API update with new files
            if hasattr(instance, '_image_files_changed') and instance._image_files_changed:
                image_changed = True
                logger.info(f"Service has new image files - will optimize: {instance.name}")
            else:
                # For existing services without new files, skip optimization entirely
                logger.info(f"FAST PATH: Skipping optimization - no new image files for existing service: {instance.name}")
                return
        else:
            # For new services, check if they have images to optimize
            has_icon = bool(instance.icon)
            if not has_icon:
                # Album images will be handled by ServiceImage signals
                logger.debug(f"New service created without icon - skipping optimization: {instance.name}")
                return
            
            logger.info(f"New service created with icon - queuing optimization: {instance.name}")
        
        # Queue optimization asynchronously - this is instantaneous and non-blocking
        AsyncImageOptimizer.queue_service_optimization(
            service_id=instance.id,
            operation_type='create' if created else 'update'
        )
        
        # Clear cache since we're processing image optimization
        cache_key = f"service_{instance.id}_images"
        cache.delete(cache_key)
        
    except Exception as e:
        logger.error(f"Error in service image optimization signal: {str(e)}")

@receiver(post_save, sender=ProjectImage)
def optimize_project_album_image_on_save(sender, instance, created, **kwargs):
    """
    Automatically optimize project album images when they are created or updated
    OPTIMIZED: Uses async queue system, only triggers for single uploads
    """
    try:
        if created and instance.project:
            # Prevent duplicate optimization with lock
            with optimization_lock:
                project_key = f"project_{instance.project.id}"
                if project_key in currently_optimizing:
                    logger.info(f"Skipping album image optimization - project already optimizing: {instance.project.title}")
                    return
            
            # Check if this is part of a bulk upload (multiple images created rapidly)
            recent_images = ProjectImage.objects.filter(
                project=instance.project,
                id__gte=instance.id - 10  # Check last 10 IDs
            ).count()
            
            if recent_images > 3:  # Likely bulk upload, skip individual optimization
                logger.info(f"Skipping individual optimization for album image {instance.id} - appears to be bulk upload")
                return
            
            # Single image upload - queue optimization asynchronously
            AsyncImageOptimizer.queue_project_optimization(
                project_id=instance.project.id,
                operation_type='album_image_create'
            )
            logger.info(f"Queued single album image optimization for project: {instance.project.title}")
            
        # Clear cache for the parent project
        if instance.project:
            cache_key = f"project_{instance.project.id}_images"
            cache.delete(cache_key)
            
    except Exception as e:
        logger.error(f"Error in project album image optimization signal: {str(e)}")

@receiver(post_save, sender=ServiceImage)
def optimize_service_album_image_on_save(sender, instance, created, **kwargs):
    """
    Automatically optimize service album images when they are created or updated
    OPTIMIZED: Uses async queue system, only triggers for single uploads
    """
    try:
        if created and instance.service:
            # Prevent duplicate optimization with lock
            with optimization_lock:
                service_key = f"service_{instance.service.id}"
                if service_key in currently_optimizing:
                    logger.info(f"Skipping album image optimization - service already optimizing: {instance.service.name}")
                    return
            
            # Check if this is part of a bulk upload (multiple images created rapidly)
            recent_images = ServiceImage.objects.filter(
                service=instance.service,
                id__gte=instance.id - 10  # Check last 10 IDs
            ).count()
            
            if recent_images > 3:  # Likely bulk upload, skip individual optimization
                logger.info(f"Skipping individual optimization for album image {instance.id} - appears to be bulk upload")
                return
            
            # Single image upload - queue optimization asynchronously
            AsyncImageOptimizer.queue_service_optimization(
                service_id=instance.service.id,
                operation_type='album_image_create'
            )
            logger.info(f"Queued single album image optimization for service: {instance.service.name}")
            
        # Clear cache for the parent service
        if instance.service:
            cache_key = f"service_{instance.service.id}_images"
            cache.delete(cache_key)
            
    except Exception as e:
        logger.error(f"Error in service album image optimization signal: {str(e)}")

@receiver(pre_save, sender=Project)
def handle_project_title_change(sender, instance, **kwargs):
    """
    Handle project title changes and cleanup old optimized images
    """
    try:
        if instance.pk:  # Only for existing projects
            try:
                old_instance = Project.objects.get(pk=instance.pk)
                if old_instance.title != instance.title:
                    # Get old folder path using ImageOptimizer method
                    old_folder_path = ImageOptimizer._get_project_folder(old_instance)
                    
                    # Clean up old optimized images
                    if os.path.exists(old_folder_path):
                        ImageOptimizer.cleanup_old_optimized_images(old_folder_path)
                        logger.info(f"Cleaned up old optimized images for project: {old_instance.title}")
                        
            except Project.DoesNotExist:
                pass
                
    except Exception as e:
        logger.error(f"Error handling project title change: {str(e)}")

@receiver(pre_save, sender=Service)
def handle_service_name_change(sender, instance, **kwargs):
    """
    Handle service name changes and cleanup old optimized images
    """
    try:
        if instance.pk:  # Only for existing services
            try:
                old_instance = Service.objects.get(pk=instance.pk)
                if old_instance.name != instance.name:
                    # Get old folder path using ImageOptimizer method
                    old_folder_path = ImageOptimizer._get_service_folder(old_instance)
                    
                    # Clean up old optimized images
                    if os.path.exists(old_folder_path):
                        ImageOptimizer.cleanup_old_optimized_images(old_folder_path)
                        logger.info(f"Cleaned up old optimized images for service: {old_instance.name}")
                        
            except Service.DoesNotExist:
                pass
                
    except Exception as e:
        logger.error(f"Error handling service name change: {str(e)}")

@receiver(post_delete, sender=Project)
def cleanup_project_images_on_delete(sender, instance, **kwargs):
    """
    Clean up entire project folder when a project is deleted
    """
    try:
        # Use the ImageOptimizer method to delete the entire project folder
        success = ImageOptimizer.delete_project_folder(instance)
        
        if success:
            logger.info(f"Successfully deleted project folder for: {instance.title}")
        else:
            logger.warning(f"Project folder deletion failed or folder didn't exist for: {instance.title}")
            
    except Exception as e:
        logger.error(f"Error deleting project folder for {instance.title}: {str(e)}")
        # Try to get basic folder path as fallback
        try:
            from django.utils.text import slugify
            project_folder_name = slugify(instance.title)[:50]
            project_folder_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_folder_name)
            if os.path.exists(project_folder_path):
                shutil.rmtree(project_folder_path)
                logger.info(f"Fallback deletion successful for project folder: {project_folder_path}")
        except Exception as fallback_error:
            logger.error(f"Fallback deletion also failed for {instance.title}: {str(fallback_error)}")

@receiver(post_delete, sender=Service)
def cleanup_service_images_on_delete(sender, instance, **kwargs):
    """
    Clean up entire service folder when a service is deleted
    """
    try:
        # Use the ImageOptimizer method to delete the entire service folder
        success = ImageOptimizer.delete_service_folder(instance)
        
        if success:
            logger.info(f"Successfully deleted service folder for: {instance.name}")
        else:
            logger.warning(f"Service folder deletion failed or folder didn't exist for: {instance.name}")
            
    except Exception as e:
        logger.error(f"Error deleting service folder for {instance.name}: {str(e)}")
        # Try to get basic folder path as fallback
        try:
            from django.utils.text import slugify
            service_folder_name = slugify(instance.name)[:50]
            service_folder_path = os.path.join(settings.MEDIA_ROOT, 'services', service_folder_name)
            if os.path.exists(service_folder_path):
                shutil.rmtree(service_folder_path)
                logger.info(f"Fallback deletion successful for service folder: {service_folder_path}")
        except Exception as fallback_error:
            logger.error(f"Fallback deletion also failed for {instance.name}: {str(fallback_error)}")

# Individual image deletion signals
@receiver(post_delete, sender=ProjectImage)
def cleanup_project_album_image_on_delete(sender, instance, **kwargs):
    """
    Clean up individual project album image file when deleted
    """
    try:
        if instance.image:
            # Use the ImageOptimizer method to delete the image file and its optimized versions
            success = ImageOptimizer.delete_image_file(instance.image)
            
            if success:
                logger.info(f"Successfully deleted project album image file and optimized versions for: {instance.image.name}")
            else:
                logger.warning(f"Project album image deletion failed or file didn't exist: {instance.image.name}")
                
    except Exception as e:
        logger.error(f"Error deleting project album image file: {str(e)}")

@receiver(post_delete, sender=ServiceImage)
def cleanup_service_album_image_on_delete(sender, instance, **kwargs):
    """
    Clean up individual service album image file when deleted
    """
    try:
        if instance.image:
            # Use the ImageOptimizer method to delete the image file and its optimized versions
            success = ImageOptimizer.delete_image_file(instance.image)
            
            if success:
                logger.info(f"Successfully deleted service album image file and optimized versions for: {instance.image.name}")
            else:
                logger.warning(f"Service album image deletion failed or file didn't exist: {instance.image.name}")
                
    except Exception as e:
        logger.error(f"Error deleting service album image file: {str(e)}")

# Cache management signals
@receiver(post_save, sender=Project)
def clear_project_cache(sender, instance, **kwargs):
    """Clear cache when projects are updated"""
    try:
        # Clear project list cache
        cache.delete('projects_list')
        cache.delete('featured_projects')
        
        # Clear specific project cache
        cache.delete(f'project_{instance.id}')
        cache.delete(f'project_{instance.id}_images')
        
    except Exception as e:
        logger.error(f"Error clearing project cache: {str(e)}")

@receiver(post_save, sender=Service)
def clear_service_cache(sender, instance, **kwargs):
    """Clear cache when services are updated"""
    try:
        # Clear service list cache
        cache.delete('services_list')
        cache.delete('featured_services')
        
        # Clear specific service cache
        cache.delete(f'service_{instance.id}')
        cache.delete(f'service_{instance.id}_images')
        
    except Exception as e:
        logger.error(f"Error clearing service cache: {str(e)}")
