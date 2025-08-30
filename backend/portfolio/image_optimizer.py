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
    
    Thumbnail Creation Methods:
    - 'fit': Crops images to exact dimensions (original behavior)
    - 'thumbnail': Scales images to fit within dimensions while preserving aspect ratio (default)
    - 'padded': Scales images to fit within dimensions and adds white padding to maintain exact dimensions
    
    Configuration:
    - THUMBNAIL_METHOD: Choose the thumbnail creation method
    - THUMBNAIL_SIZES: Define the maximum dimensions for each size
    - WEBP_QUALITY: Quality setting for WebP compression (85 = high quality)
    
    Usage:
    - Set THUMBNAIL_METHOD to 'thumbnail' for no cropping (recommended for most use cases)
    - Set THUMBNAIL_METHOD to 'padded' if you need consistent dimensions with padding
    - Set THUMBNAIL_METHOD to 'fit' if you need exact dimensions and cropping is acceptable
    """
    
    # Quality settings - optimized for web while maintaining visual quality
    WEBP_QUALITY = 85  # High quality WebP
    JPEG_QUALITY = 88  # High quality JPEG
    
    # Thumbnail creation method: 'fit' (crops to exact size), 'thumbnail' (preserves aspect ratio), 'padded' (adds padding)
    THUMBNAIL_METHOD = 'thumbnail'  # Options: 'fit', 'thumbnail', 'padded'
    
    # Thumbnail sizes for different use cases
    # These are maximum dimensions - images will be scaled down to fit within these bounds
    # while preserving their aspect ratio (no cropping)
    THUMBNAIL_SIZES = {
        'small': (300, 300),      # For thumbnails and previews
        'medium': (800, 800),     # For medium displays (increased from 600)
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
            
            # Update the project model with optimized image paths
            cls._update_project_optimized_paths(project, webp_folder, name_without_ext)
            
            logger.info(f"Optimized main image for project: {project.title}")
            
        except Exception as e:
            logger.error(f"Error optimizing main image for project {project.title}: {str(e)}")
    
    @classmethod
    def _update_project_optimized_paths(cls, project, webp_folder, base_name):
        """Update the project model with optimized image paths"""
        try:
            from django.conf import settings
            
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the project model fields - main images are in webp/ folder
            project.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            project.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            project.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            project.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_project_images_on_save
            post_save.disconnect(optimize_project_images_on_save, sender=type(project))
            
            try:
                project.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_project_images_on_save, sender=type(project))
                
            logger.info(f"Updated optimized image paths for project: {project.title}")
            
        except Exception as e:
            logger.error(f"Error updating optimized image paths for project {project.title}: {str(e)}")
    
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
            
            # Update the album image model with optimized image paths
            cls._update_project_album_optimized_paths(album_image, webp_album_folder, name_without_ext)
            
            logger.info(f"Optimized album image: {original_filename}")
            
        except Exception as e:
            logger.error(f"Error optimizing album image {album_image.image.name}: {str(e)}")
    
    @classmethod
    def _update_project_album_optimized_paths(cls, album_image, webp_folder, base_name):
        """Update the project album image model with optimized image paths"""
        try:
            from django.conf import settings
            
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the album image model fields - album images are in webp/album/ folder
            album_image.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            album_image.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            album_image.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            album_image.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_project_album_image_on_save
            post_save.disconnect(optimize_project_album_image_on_save, sender=type(album_image))
            
            try:
                album_image.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_project_album_image_on_save, sender=type(album_image))
                
            logger.info(f"Updated optimized image paths for album image: {album_image.id}")
            
        except Exception as e:
            logger.error(f"Error updating optimized image paths for album image {album_image.id}: {str(e)}")
    
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
            
            # Update the service model with optimized icon paths
            cls._update_service_optimized_paths(service, webp_folder, name_without_ext)
            
            logger.info(f"Optimized icon for service: {service.name}")
            
        except Exception as e:
            logger.error(f"Error optimizing icon for service {service.name}: {str(e)}")
    
    @classmethod
    def _update_service_optimized_paths(cls, service, webp_folder, base_name):
        """Update the service model with optimized icon paths"""
        try:
            from django.conf import settings
            
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the service model fields
            service.optimized_icon = f"{webp_folder_rel}/{base_name}.webp"
            service.optimized_icon_small = f"{webp_folder_rel}/{base_name}_small.webp"
            service.optimized_icon_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            service.optimized_icon_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_service_images_on_save
            post_save.disconnect(optimize_service_images_on_save, sender=type(service))
            
            try:
                service.save(update_fields=[
                    'optimized_icon', 'optimized_icon_small', 
                    'optimized_icon_medium', 'optimized_icon_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_service_images_on_save, sender=type(service))
                
            logger.info(f"Updated optimized icon paths for service: {service.name}")
            
        except Exception as e:
            logger.error(f"Error updating optimized icon paths for service {service.name}: {str(e)}")
    
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
            
            # Update the service album image model with optimized image paths
            cls._update_service_album_optimized_paths(album_image, webp_album_folder, name_without_ext)
            
            logger.info(f"Optimized service album image: {original_filename}")
            
        except Exception as e:
            logger.error(f"Error optimizing service album image {album_image.image.name}: {str(e)}")
    
    @classmethod
    def _update_service_album_optimized_paths(cls, album_image, webp_folder, base_name):
        """Update the service album image model with optimized image paths"""
        try:
            from django.conf import settings
            
            # Get relative paths for database storage
            media_root = settings.MEDIA_ROOT
            webp_folder_rel = os.path.relpath(webp_folder, media_root)
            
            # Update the album image model fields - service album images are in webp/album/ folder
            album_image.optimized_image = f"{webp_folder_rel}/{base_name}.webp"
            album_image.optimized_image_small = f"{webp_folder_rel}/{base_name}_small.webp"
            album_image.optimized_image_medium = f"{webp_folder_rel}/{base_name}_medium.webp"
            album_image.optimized_image_large = f"{webp_folder_rel}/{base_name}_large.webp"
            
            # Save without triggering signals
            from django.db.models.signals import post_save
            from .signals import optimize_service_album_image_on_save
            post_save.disconnect(optimize_service_album_image_on_save, sender=type(album_image))
            
            try:
                album_image.save(update_fields=[
                    'optimized_image', 'optimized_image_small', 
                    'optimized_image_medium', 'optimized_image_large'
                ])
            finally:
                # Reconnect the signal
                post_save.connect(optimize_service_album_image_on_save, sender=type(album_image))
                
            logger.info(f"Updated optimized image paths for service album image: {album_image.id}")
            
        except Exception as e:
            logger.error(f"Error updating optimized image paths for service album image {album_image.id}: {str(e)}")
    
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
                    
                    # Choose thumbnail creation method based on configuration
                    if cls.THUMBNAIL_METHOD == 'fit':
                        # Original method - crops to exact size
                        thumbnail = ImageOps.fit(img, dimensions, method=Image.Resampling.LANCZOS)
                    elif cls.THUMBNAIL_METHOD == 'padded':
                        # Method with padding to maintain dimensions
                        thumbnail = cls._create_single_padded_thumbnail(img, dimensions)
                    else:
                        # Default method - preserves aspect ratio (no cropping)
                        thumbnail = img.copy()
                        thumbnail.thumbnail(dimensions, Image.Resampling.LANCZOS)
                    
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
    def _create_single_padded_thumbnail(cls, img, dimensions):
        """Create a single padded thumbnail"""
        # Calculate scaling factor to fit within dimensions
        img_ratio = img.width / img.height
        target_ratio = dimensions[0] / dimensions[1]
        
        if img_ratio > target_ratio:
            # Image is wider than target - scale by width
            new_width = dimensions[0]
            new_height = int(dimensions[0] / img_ratio)
        else:
            # Image is taller than target - scale by height
            new_height = dimensions[1]
            new_width = int(dimensions[1] * img_ratio)
        
        # Resize image
        thumbnail = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with target dimensions and white background
        final_thumbnail = Image.new('RGB', dimensions, (255, 255, 255))
        
        # Calculate position to center the thumbnail
        x = (dimensions[0] - new_width) // 2
        y = (dimensions[1] - new_height) // 2
        
        # Paste the thumbnail onto the background
        final_thumbnail.paste(thumbnail, (x, y))
        
        return final_thumbnail
    
    @classmethod
    def _create_thumbnails_with_padding(cls, original_path, output_folder, base_name, image_type):
        """Create thumbnails with padding to maintain consistent dimensions"""
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
                    
                    # Calculate scaling factor to fit within dimensions
                    img_ratio = img.width / img.height
                    target_ratio = dimensions[0] / dimensions[1]
                    
                    if img_ratio > target_ratio:
                        # Image is wider than target - scale by width
                        new_width = dimensions[0]
                        new_height = int(dimensions[0] / img_ratio)
                    else:
                        # Image is taller than target - scale by height
                        new_height = dimensions[1]
                        new_width = int(dimensions[1] * img_ratio)
                    
                    # Resize image
                    thumbnail = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create new image with target dimensions and white background
                    final_thumbnail = Image.new('RGB', dimensions, (255, 255, 255))
                    
                    # Calculate position to center the thumbnail
                    x = (dimensions[0] - new_width) // 2
                    y = (dimensions[1] - new_height) // 2
                    
                    # Paste the thumbnail onto the background
                    final_thumbnail.paste(thumbnail, (x, y))
                    
                    # Save as WebP
                    webp_filename = f"{base_name}_{size_name}_padded.webp"
                    webp_path = os.path.join(output_folder, webp_filename)
                    final_thumbnail.save(webp_path, 'WEBP', quality=cls.WEBP_QUALITY, method=6)
                    
                    # Set proper permissions
                    os.chmod(webp_path, 0o644)
                    
        except Exception as e:
            logger.error(f"Error creating padded thumbnails for {original_path}: {str(e)}")
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

    @classmethod
    def delete_project_folder(cls, project):
        """
        Completely delete a project folder and all its contents
        """
        try:
            project_folder = cls._get_project_folder(project)
            
            if os.path.exists(project_folder):
                import shutil
                shutil.rmtree(project_folder)
                logger.info(f"Completely deleted project folder: {project_folder}")
                return True
            else:
                logger.info(f"Project folder does not exist: {project_folder}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting project folder for {project.title}: {str(e)}")
            return False

    @classmethod
    def delete_service_folder(cls, service):
        """
        Completely delete a service folder and all its contents
        """
        try:
            service_folder = cls._get_service_folder(service)
            
            if os.path.exists(service_folder):
                import shutil
                shutil.rmtree(service_folder)
                logger.info(f"Completely deleted service folder: {service_folder}")
                return True
            else:
                logger.info(f"Service folder does not exist: {service_folder}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting service folder for {service.name}: {str(e)}")
            return False

    @classmethod
    def delete_image_file(cls, image_field):
        """
        Delete an individual image file and its optimized versions
        """
        try:
            if not image_field:
                return False
                
            # Get the original image path
            original_path = image_field.path
            
            if os.path.exists(original_path):
                # Delete the original file
                os.remove(original_path)
                logger.info(f"Deleted original image file: {original_path}")
                
                # Try to delete optimized versions if they exist
                try:
                    # Get the directory and filename
                    image_dir = os.path.dirname(original_path)
                    image_filename = os.path.basename(original_path)
                    name_without_ext = os.path.splitext(image_filename)[0]
                    
                    # Check for webp folder
                    webp_folder = os.path.join(image_dir, 'webp')
                    if os.path.exists(webp_folder):
                        # Look for optimized versions
                        for size_name in cls.THUMBNAIL_SIZES.keys():
                            if size_name != 'original':
                                webp_path = os.path.join(webp_folder, f"{name_without_ext}_{size_name}.webp")
                                if os.path.exists(webp_path):
                                    os.remove(webp_path)
                                    logger.info(f"Deleted optimized image: {webp_path}")
                                
                                # Also check for padded versions
                                padded_path = os.path.join(webp_folder, f"{name_without_ext}_{size_name}_padded.webp")
                                if os.path.exists(padded_path):
                                    os.remove(padded_path)
                                    logger.info(f"Deleted padded image: {padded_path}")
                        
                        # Check for main webp version
                        main_webp = os.path.join(webp_folder, f"{name_without_ext}.webp")
                        if os.path.exists(main_webp):
                            os.remove(main_webp)
                            logger.info(f"Deleted main webp image: {main_webp}")
                            
                except Exception as webp_error:
                    logger.warning(f"Error cleaning up optimized images: {str(webp_error)}")
                
                return True
            else:
                logger.info(f"Image file does not exist: {original_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting image file: {str(e)}")
            return False
