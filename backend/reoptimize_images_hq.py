#!/usr/bin/env python
"""
Re-optimize all existing images with new high-quality settings
This script will regenerate all optimized versions with better quality
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project, Service, ProjectImage, ServiceImage
from portfolio.image_optimizer import ImageOptimizer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reoptimize_all_images():
    """Re-optimize all images with new high-quality settings"""
    
    logger.info("🚀 Starting high-quality image re-optimization...")
    
    # Re-optimize project images
    logger.info("📸 Re-optimizing project images...")
    projects = Project.objects.all()
    for project in projects:
        if project.image:
            try:
                logger.info(f"Processing project: {project.title}")
                ImageOptimizer.save_optimized_versions(project.image.name)
            except Exception as e:
                logger.error(f"Error processing project {project.title}: {e}")
    
    # Re-optimize service images
    logger.info("🔧 Re-optimizing service images...")
    services = Service.objects.all()
    for service in services:
        if service.icon:
            try:
                logger.info(f"Processing service: {service.name}")
                ImageOptimizer.save_optimized_versions(service.icon.name)
            except Exception as e:
                logger.error(f"Error processing service {service.name}: {e}")
    
    # Re-optimize project album images
    logger.info("🖼️ Re-optimizing project album images...")
    project_images = ProjectImage.objects.all()
    for img in project_images:
        if img.image:
            try:
                logger.info(f"Processing project image: {img.id}")
                ImageOptimizer.save_optimized_versions(img.image.name)
            except Exception as e:
                logger.error(f"Error processing project image {img.id}: {e}")
    
    # Re-optimize service album images
    logger.info("🖼️ Re-optimizing service album images...")
    service_images = ServiceImage.objects.all()
    for img in service_images:
        if img.image:
            try:
                logger.info(f"Processing service image: {img.id}")
                ImageOptimizer.save_optimized_versions(img.image.name)
            except Exception as e:
                logger.error(f"Error processing service image {img.id}: {e}")
    
    logger.info("✅ High-quality image re-optimization complete!")

if __name__ == "__main__":
    reoptimize_all_images()
