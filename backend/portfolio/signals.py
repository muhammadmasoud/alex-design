"""
Django signals for automatic image optimization and cleanup
"""
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from rest_framework.authtoken.models import Token
from django.utils.text import slugify
from .models import Project, Service, User, ProjectImage, ServiceImage
from .image_utils import optimize_image, should_optimize_image
import os


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=Project)
def optimize_and_cleanup_project_image(sender, instance, **kwargs):
    """
    Optimize new project images and delete old ones
    """
    # Create project folders on first save
    if not instance.pk and instance.title:
        instance._create_project_folders()
    
    # Delete old image if updating
    if instance.pk:
        try:
            old_instance = Project.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                try:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
                except (ValueError, OSError):
                    pass
        except Project.DoesNotExist:
            pass
    
    # Optimize new image
    if instance.image and hasattr(instance.image, 'file'):
        is_new_image = True
        if instance.pk:
            try:
                old_instance = Project.objects.get(pk=instance.pk)
                if old_instance.image and old_instance.image.name == instance.image.name:
                    is_new_image = False
            except Project.DoesNotExist:
                pass
        
        if is_new_image and should_optimize_image(instance.image):
            optimized = optimize_image(
                instance.image,
                max_width=1920,
                max_height=1080,
                quality=85
            )
            if optimized:
                instance.image = optimized


@receiver(pre_save, sender=Service)
def optimize_and_cleanup_service_icon(sender, instance, **kwargs):
    """
    Optimize new service icons and delete old ones
    """
    # Delete old icon if updating
    if instance.pk:
        try:
            old_instance = Service.objects.get(pk=instance.pk)
            if old_instance.icon and old_instance.icon != instance.icon:
                try:
                    if os.path.isfile(old_instance.icon.path):
                        os.remove(old_instance.icon.path)
                except (ValueError, OSError):
                    pass
        except Service.DoesNotExist:
            pass
    
    # Optimize new icon
    if instance.icon and hasattr(instance.icon, 'file'):
        is_new_icon = True
        if instance.pk:
            try:
                old_instance = Service.objects.get(pk=instance.pk)
                if old_instance.icon and old_instance.icon.name == instance.icon.name:
                    is_new_icon = False
            except Service.DoesNotExist:
                pass
        
        if is_new_icon and should_optimize_image(instance.icon):
            optimized = optimize_image(
                instance.icon,
                max_width=512,
                max_height=512,
                quality=90
            )
            if optimized:
                instance.icon = optimized


@receiver(pre_save, sender=ProjectImage)
def optimize_and_cleanup_project_album_image(sender, instance, **kwargs):
    """
    Optimize new project album images and delete old ones
    """
    # Ensure album folder exists before saving
    if instance.project and instance.project.title:
        instance._ensure_album_folder_exists()
    
    # Delete old image if updating
    if instance.pk:
        try:
            old_instance = ProjectImage.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                try:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
                except (ValueError, OSError):
                    pass
        except ProjectImage.DoesNotExist:
            pass
    
    # Optimize new image
    if instance.image and hasattr(instance.image, 'file'):
        is_new_image = True
        if instance.pk:
            try:
                old_instance = ProjectImage.objects.get(pk=instance.pk)
                if old_instance.image and old_instance.image.name == instance.image.name:
                    is_new_image = False
            except ProjectImage.DoesNotExist:
                pass
        
        if is_new_image and should_optimize_image(instance.image):
            optimized = optimize_image(
                instance.image,
                max_width=1920,
                max_height=1080,
                quality=80
            )
            if optimized:
                instance.image = optimized


@receiver(pre_save, sender=ServiceImage)
def optimize_and_cleanup_service_album_image(sender, instance, **kwargs):
    """
    Optimize new service album images and delete old ones
    """
    # Delete old image if updating
    if instance.pk:
        try:
            old_instance = ServiceImage.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                try:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
                except (ValueError, OSError):
                    pass
        except ServiceImage.DoesNotExist:
            pass
    
    # Optimize new image
    if instance.image and hasattr(instance.image, 'file'):
        is_new_image = True
        if instance.pk:
            try:
                old_instance = ServiceImage.objects.get(pk=instance.pk)
                if old_instance.image and old_instance.image.name == instance.image.name:
                    is_new_image = False
            except ServiceImage.DoesNotExist:
                pass
        
        if is_new_image and should_optimize_image(instance.image):
            optimized = optimize_image(
                instance.image,
                max_width=1920,
                max_height=1080,
                quality=80
            )
            if optimized:
                instance.image = optimized


@receiver(post_delete, sender=Project)
def delete_project_files(sender, instance, **kwargs):
    """Delete project image file and all related album images when project is deleted"""
    import shutil
    from django.conf import settings
    
    # Delete main project image
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass
    
    # Delete all related album images (cascade delete will handle the model instances)
    for album_image in instance.album_images.all():
        if album_image.image:
            try:
                if os.path.isfile(album_image.image.path):
                    os.remove(album_image.image.path)
            except (ValueError, OSError):
                pass
    
    # Delete entire project folder if it exists
    if instance.title:
        try:
            project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', slugify(instance.title))
            if os.path.exists(project_folder):
                shutil.rmtree(project_folder)
                print(f"Deleted project folder: {project_folder}")
        except Exception as e:
            print(f"Error deleting project folder: {e}")


@receiver(post_delete, sender=Service)
def delete_service_files(sender, instance, **kwargs):
    """Delete service icon file and all related album images when service is deleted"""
    # Delete main service icon
    if instance.icon:
        try:
            if os.path.isfile(instance.icon.path):
                os.remove(instance.icon.path)
        except (ValueError, OSError):
            pass
    
    # Delete all related album images (cascade delete will handle the model instances)
    for album_image in instance.album_images.all():
        if album_image.image:
            try:
                if os.path.isfile(album_image.image.path):
                    os.remove(album_image.image.path)
            except (ValueError, OSError):
                pass


@receiver(post_delete, sender=ProjectImage)
def delete_project_album_image(sender, instance, **kwargs):
    """Delete project album image file when ProjectImage is deleted"""
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass


@receiver(post_delete, sender=ServiceImage)
def delete_service_album_image(sender, instance, **kwargs):
    """Delete service album image file when ServiceImage is deleted"""
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass
