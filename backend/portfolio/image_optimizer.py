"""
Image Optimization Utilities for Alex Design Portfolio
Handles automatic image optimization while maintaining quality and organizing files properly
"""

import os
import logging
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageOptimizer:
    """
    Handles automatic image optimization for projects and services
    Creates organized folder structure with optimized images
    """
    
    # Quality settings - optimized for web while maintaining visual quality
    WEBP_QUALITY = 85  # High quality WebP
    JPEG_QUALITY = 88  # High quality JPEG
    
    # Thumbnail sizes for different use cases
    THUMBNAIL_SIZES = {
        'small': (300, 300),      # For thumbnails and previews
        'medium': (600, 600),     # For medium displays
        'large': (1200, 1200),    # For large displays
        'original': None           # Keep original size
    }
    
    @classmethod
    def optimize_project_images(cls, project):
        """
        Optimize all images for a project (main image + album images)
        Creates organized folder structure with optimized versions
        """
        try:
            project_folder = cls._get_project_folder(project)
            
            # Optimize main image if exists
            if project.image:
                cls._optimize_main_image(project, project_folder)
            
            # Optimize album images
            for album_image in project.album_images.all():
                cls._optimize_album_image(album_image, project_folder)
                
            logger.info(f"Successfully optimized all images for project: {project.title}")
            
        except Exception as e:
            logger.error(f"Error optimizing project images for {project.title}: {str(e)}")
            # Don't fail the project creation if optimization fails
    
    @classmethod
    def optimize_service_images(cls, service):
        """
        Optimize all images for a service (icon + album images)
        Creates organized folder structure with optimized versions
        """
        try:
            service_folder = cls._get_service_folder(service)
            
            # Optimize icon if exists
            if service.icon:
                cls._optimize_service_icon(service, service_folder)
            
            # Optimize album images
            for album_image in service.album_images.all():
                cls._optimize_service_album_image(album_image, service_folder)
                
            logger.info(f"Successfully optimized all images for service: {service.name}")
            
        except Exception as e:
            logger.error(f"Error optimizing service images for {service.name}: {str(e)}")
            # Don't fail the service creation if optimization fails
    
    @classmethod
    def _get_project_folder(cls, project):
        """Get the project folder path"""
        from django.utils.text import slugify
        project_name = slugify(project.title)[:50]
        return os.path.join(settings.MEDIA_ROOT, 'projects', project_name)
    
    @classmethod
    def _get_service_folder(cls, service):
        """Get the service folder path"""
        from django.utils.text import slugify
        service_name = slugify(service.name)[:50]
        return os.path.join(settings.MEDIA_ROOT, 'services', service_name)
    
    @classmethod
    def _optimize_main_image(cls, project, project_folder):
        """Optimize the main project image"""
        try:
            # Create webp folder
            webp_folder = os.path.join(project_folder, 'webp')
            os.makedirs(webp_folder, exist_ok=True)
            
            # Get original image info
            original_path = project.image.path
            original_filename = os.path.basename(original_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            
            # Create optimized WebP version
            webp_path = os.path.join(webp_folder, f"{name_without_ext}.webp")
            cls._create_optimized_webp(original_path, webp_path, 'main')
            
            # Create thumbnails
            cls._create_thumbnails(original_path, webp_folder, name_without_ext, 'main')
            
            logger.info(f"Optimized main image for project: {project.title}")
            
        except Exception as e:
            logger.error(f"Error optimizing main image for project {project.title}: {str(e)}")
    
    @classmethod
    def _optimize_album_image(cls, album_image, project_folder):
        """Optimize a project album image"""
        try:
            # Create webp/album folder
            webp_album_folder = os.path.join(project_folder, 'webp', 'album')
            os.makedirs(webp_album_folder, exist_ok=True)
            
            # Get original image info
            original_path = album_image.image.path
            original_filename = os.path.basename(original_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            
            # Create optimized WebP version
            webp_path = os.path.join(webp_album_folder, f"{name_without_ext}.webp")
            cls._create_optimized_webp(original_path, webp_path, 'album')
            
            # Create thumbnails
            cls._create_thumbnails(original_path, webp_album_folder, name_without_ext, 'album')
            
            logger.info(f"Optimized album image: {original_filename}")
            
        except Exception as e:
            logger.error(f"Error optimizing album image {album_image.image.name}: {str(e)}")
    
    @classmethod
    def _optimize_service_icon(cls, service, service_folder):
        """Optimize the service icon"""
        try:
            # Create webp folder
            webp_folder = os.path.join(service_folder, 'webp')
            os.makedirs(webp_folder, exist_ok=True)
            
            # Get original image info
            original_path = service.icon.path
            original_filename = os.path.basename(original_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            
            # Create optimized WebP version
            webp_path = os.path.join(webp_folder, f"{name_without_ext}.webp")
            cls._create_optimized_webp(original_path, webp_path, 'icon')
            
            # Create thumbnails
            cls._create_thumbnails(original_path, webp_folder, name_without_ext, 'icon')
            
            logger.info(f"Optimized icon for service: {service.name}")
            
        except Exception as e:
            logger.error(f"Error optimizing icon for service {service.name}: {str(e)}")
    
    @classmethod
    def _optimize_service_album_image(cls, album_image, service_folder):
        """Optimize a service album image"""
        try:
            # Create webp/album folder
            webp_album_folder = os.path.join(service_folder, 'webp', 'album')
            os.makedirs(webp_album_folder, exist_ok=True)
            
            # Get original image info
            original_path = album_image.image.path
            original_filename = os.path.basename(original_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            
            # Create optimized WebP version
            webp_path = os.path.join(webp_album_folder, f"{name_without_ext}.webp")
            cls._create_optimized_webp(original_path, webp_path, 'album')
            
            # Create thumbnails
            cls._create_thumbnails(original_path, webp_album_folder, name_without_ext, 'album')
            
            logger.info(f"Optimized service album image: {original_filename}")
            
        except Exception as e:
            logger.error(f"Error optimizing service album image {album_image.image.name}: {str(e)}")
    
    @classmethod
    def _create_optimized_webp(cls, original_path, webp_path, image_type):
        """Create optimized WebP version of the image"""
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if necessary (WebP doesn't support RGBA well)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as WebP with high quality
                img.save(webp_path, 'WEBP', quality=cls.WEBP_QUALITY, method=6)
                
                # Set proper permissions
                os.chmod(webp_path, 0o644)
                
        except Exception as e:
            logger.error(f"Error creating WebP for {original_path}: {str(e)}")
            raise
    
    @classmethod
    def _create_thumbnails(cls, original_path, output_folder, base_name, image_type):
        """Create thumbnails in different sizes"""
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create thumbnails for each size
                for size_name, dimensions in cls.THUMBNAIL_SIZES.items():
                    if dimensions is None:  # Skip original size
                        continue
                        
                    # Create thumbnail
                    thumbnail = ImageOps.fit(img, dimensions, method=Image.Resampling.LANCZOS)
                    
                    # Save as WebP
                    webp_filename = f"{base_name}_{size_name}.webp"
                    webp_path = os.path.join(output_folder, webp_filename)
                    thumbnail.save(webp_path, 'WEBP', quality=cls.WEBP_QUALITY, method=6)
                    
                    # Set proper permissions
                    os.chmod(webp_path, 0o644)
                    
        except Exception as e:
            logger.error(f"Error creating thumbnails for {original_path}: {str(e)}")
            raise
    
    @classmethod
    def get_optimized_image_url(cls, original_image_path, size='medium', format='webp'):
        """
        Get the URL for an optimized image
        Returns the path to the optimized version if it exists
        """
        try:
            if not original_image_path:
                return None
                
            # Get the directory and filename
            original_dir = os.path.dirname(original_image_path)
            original_filename = os.path.basename(original_image_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            
            # Determine the optimized path
            if format == 'webp':
                if 'album' in original_image_path:
                    # Album image
                    optimized_path = os.path.join(original_dir, 'webp', 'album', f"{name_without_ext}_{size}.webp")
                else:
                    # Main image or icon
                    optimized_path = os.path.join(original_dir, 'webp', f"{name_without_ext}_{size}.webp")
            else:
                return original_image_path  # Return original if format not supported
            
            # Check if optimized version exists
            if os.path.exists(optimized_path):
                # Convert to URL
                relative_path = os.path.relpath(optimized_path, settings.MEDIA_ROOT)
                return f"{settings.MEDIA_URL}{relative_path}"
            
            # Return original if optimized version doesn't exist
            return original_image_path
            
        except Exception as e:
            logger.error(f"Error getting optimized image URL: {str(e)}")
            return original_image_path
    
    @classmethod
    def cleanup_old_optimized_images(cls, old_folder_path):
        """
        Clean up old optimized images when project/service is moved or deleted
        """
        try:
            if os.path.exists(old_folder_path):
                webp_folder = os.path.join(old_folder_path, 'webp')
                if os.path.exists(webp_folder):
                    import shutil
                    shutil.rmtree(webp_folder)
                    logger.info(f"Cleaned up optimized images in: {old_folder_path}")
        except Exception as e:
            logger.error(f"Error cleaning up optimized images in {old_folder_path}: {str(e)}")
