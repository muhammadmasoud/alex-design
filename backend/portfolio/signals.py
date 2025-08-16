from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .models import Project, Service, User, ProjectImage, ServiceImage
import os

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_delete, sender=Project)
def delete_project_files(sender, instance, **kwargs):
    """Delete project image file and all related album images when project is deleted"""
    # Delete main project image
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid
    
    # Delete all related album images (cascade delete will handle the model instances)
    for album_image in instance.album_images.all():
        if album_image.image:
            try:
                if os.path.isfile(album_image.image.path):
                    os.remove(album_image.image.path)
            except (ValueError, OSError):
                pass  # File already deleted or path invalid

@receiver(post_delete, sender=Service)
def delete_service_files(sender, instance, **kwargs):
    """Delete service icon file and all related album images when service is deleted"""
    # Delete main service icon
    if instance.icon:
        try:
            if os.path.isfile(instance.icon.path):
                os.remove(instance.icon.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid
    
    # Delete all related album images (cascade delete will handle the model instances)
    for album_image in instance.album_images.all():
        if album_image.image:
            try:
                if os.path.isfile(album_image.image.path):
                    os.remove(album_image.image.path)
            except (ValueError, OSError):
                pass  # File already deleted or path invalid

@receiver(pre_save, sender=Project)
def delete_old_project_image(sender, instance, **kwargs):
    """Delete old project image when a new one is uploaded"""
    if not instance.pk:
        return False

    try:
        old_instance = Project.objects.get(pk=instance.pk)
    except Project.DoesNotExist:
        return False

    if old_instance.image and old_instance.image != instance.image:
        try:
            if os.path.isfile(old_instance.image.path):
                os.remove(old_instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid

@receiver(pre_save, sender=Service)
def delete_old_service_icon(sender, instance, **kwargs):
    """Delete old service icon when a new one is uploaded"""
    if not instance.pk:
        return False

    try:
        old_instance = Service.objects.get(pk=instance.pk)
    except Service.DoesNotExist:
        return False

    if old_instance.icon and old_instance.icon != instance.icon:
        try:
            if os.path.isfile(old_instance.icon.path):
                os.remove(old_instance.icon.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid

@receiver(post_delete, sender=ProjectImage)
def delete_project_album_image(sender, instance, **kwargs):
    """Delete project album image file when ProjectImage is deleted"""
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid

@receiver(post_delete, sender=ServiceImage)
def delete_service_album_image(sender, instance, **kwargs):
    """Delete service album image file when ServiceImage is deleted"""
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid

@receiver(pre_save, sender=ProjectImage)
def delete_old_project_album_image(sender, instance, **kwargs):
    """Delete old project album image when a new one is uploaded"""
    if not instance.pk:
        return False

    try:
        old_instance = ProjectImage.objects.get(pk=instance.pk)
    except ProjectImage.DoesNotExist:
        return False

    if old_instance.image and old_instance.image != instance.image:
        try:
            if os.path.isfile(old_instance.image.path):
                os.remove(old_instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid

@receiver(pre_save, sender=ServiceImage)
def delete_old_service_album_image(sender, instance, **kwargs):
    """Delete old service album image when a new one is uploaded"""
    if not instance.pk:
        return False

    try:
        old_instance = ServiceImage.objects.get(pk=instance.pk)
    except ServiceImage.DoesNotExist:
        return False

    if old_instance.image and old_instance.image != instance.image:
        try:
            if os.path.isfile(old_instance.image.path):
                os.remove(old_instance.image.path)
        except (ValueError, OSError):
            pass  # File already deleted or path invalid
