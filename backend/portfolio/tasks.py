from celery import shared_task
from .models import Project, ProjectImage
from django.core.files.base import ContentFile
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def async_bulk_upload_project_images(self, project_id, images_data, replace_existing=False):
    """
    Celery task to process bulk upload of project images asynchronously.
    images_data: list of dicts with keys: name, content (base64), content_type
    """
    try:
        project = Project.objects.get(id=project_id)
        if replace_existing:
            ProjectImage.objects.filter(project=project).delete()
        created_images = []
        with transaction.atomic():
            for i, img in enumerate(images_data):
                image_file = ContentFile(img['content'].decode('base64'), name=img['name'])
                project_image = ProjectImage.objects.create(
                    project=project,
                    image=image_file,
                    original_filename=img['name'],
                    order=i
                )
                created_images.append(project_image.id)
        logger.info(f"Bulk upload complete for project {project_id} with {len(created_images)} images.")
        return {'status': 'success', 'created_images': created_images}
    except Exception as e:
        logger.error(f"Async bulk upload failed: {e}")
        return {'status': 'error', 'error': str(e)}
