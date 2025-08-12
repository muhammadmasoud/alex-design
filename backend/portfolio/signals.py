from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .models import Project, Service, User
import os

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_delete, sender=Project)
def delete_project_image(sender, instance, **kwargs):
    """Delete project image file when project is deleted"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(post_delete, sender=Service)
def delete_service_icon(sender, instance, **kwargs):
    """Delete service icon file when service is deleted"""
    if instance.icon:
        if os.path.isfile(instance.icon.path):
            os.remove(instance.icon.path)

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
        if os.path.isfile(old_instance.image.path):
            os.remove(old_instance.image.path)

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
        if os.path.isfile(old_instance.icon.path):
            os.remove(old_instance.icon.path)
