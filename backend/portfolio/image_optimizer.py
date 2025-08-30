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

# Import configuration
try:
    from .image_optimizer_config import *
except ImportError:
    # Fallback configuration if config file doesn't exist
    PRODUCTION_MODE = True
    PRODUCTION_WEBP_QUALITY = 100
    PRODUCTION_JPEG_QUALITY = 100
    PRODUCTION_WEBP_LOSSLESS = True
    PRODUCTION_WEBP_METHOD = 6
    DEVELOPMENT_WEBP_QUALITY = 95
    DEVELOPMENT_JPEG_QUALITY = 95
    DEVELOPMENT_WEBP_LOSSLESS = False
    DEVELOPMENT_WEBP_METHOD = 4
    THUMBNAIL_METHOD = 'thumbnail'
    THUMBNAIL_SIZES = {
        'small': (400, 400),
        'medium': (1000, 1000),
        'large': (1600, 1600),
        'original': None
    }
    # Advanced settings
    PRESERVE_METADATA = True
    PRESERVE_TRANSPARENCY = True
    USE_SHARP_YUVA = False  # Disabled for AWS compatibility
    ALPHA_QUALITY = 100
    THUMBNAIL_SHARPENING = False  # Disabled for AWS compatibility
    PRESERVE_ICC_PROFILE = True
    # AWS compatibility settings
    AWS_SAFE_MODE = True
    SKIP_ADVANCED_FEATURES = True

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
    - PRODUCTION_MODE: Set to True for production (lossless), False for development (faster)
    - WEBP_QUALITY: Quality setting for WebP compression (100 = lossless for production)
    - WEBP_LOSSLESS: Enable lossless WebP encoding for maximum quality preservation
    - WEBP_METHOD: WebP compression method (6 = best quality, slowest)
    - AWS_SAFE_MODE: Enable AWS-safe mode with fallbacks
    
    Usage:
    - Set PRODUCTION_MODE = True for production use (0% quality loss, slower processing)
    - Set PRODUCTION_MODE = False for development (faster processing, high quality)
    - Set THUMBNAIL_METHOD to 'thumbnail' for no cropping (recommended for most use cases)
    - Set THUMBNAIL_METHOD to 'padded' if you need consistent dimensions with padding
    - Set THUMBNAIL_METHOD to 'fit' if you need exact dimensions and cropping is acceptable
    - WEBP_LOSSLESS=True ensures 0% quality loss for production use
    - AWS_SAFE_MODE=True ensures compatibility with AWS environments
    """
    
    # Quality settings - imported from configuration
    WEBP_QUALITY = PRODUCTION_WEBP_QUALITY if PRODUCTION_MODE else DEVELOPMENT_WEBP_QUALITY
    JPEG_QUALITY = PRODUCTION_JPEG_QUALITY if PRODUCTION_MODE else DEVELOPMENT_JPEG_QUALITY
    WEBP_LOSSLESS = PRODUCTION_WEBP_LOSSLESS if PRODUCTION_MODE else DEVELOPMENT_WEBP_LOSSLESS
    WEBP_METHOD = PRODUCTION_WEBP_METHOD if PRODUCTION_MODE else DEVELOPMENT_WEBP_METHOD
    
    # Production mode - imported from configuration
    PRODUCTION_MODE = PRODUCTION_MODE
    
    # Thumbnail creation method - imported from configuration
    THUMBNAIL_METHOD = THUMBNAIL_METHOD
    
    # Thumbnail sizes - imported from configuration
    THUMBNAIL_SIZES = THUMBNAIL_SIZES
    
    # AWS compatibility settings - imported from configuration
    AWS_SAFE_MODE = AWS_SAFE_MODE if 'AWS_SAFE_MODE' in globals() else True
    SKIP_ADVANCED_FEATURES = SKIP_ADVANCED_FEATURES if 'SKIP_ADVANCED_FEATURES' in globals() else True
    
    # Advanced quality settings - imported from configuration
    PRESERVE_METADATA = PRESERVE_METADATA if 'PRESERVE_METADATA' in globals() else True
    PRESERVE_TRANSPARENCY = PRESERVE_TRANSPARENCY if 'PRESERVE_TRANSPARENCY' in globals() else True
    USE_SHARP_YUVA = USE_SHARP_YUVA if 'USE_SHARP_YUVA' in globals() else False
    ALPHA_QUALITY = ALPHA_QUALITY if 'ALPHA_QUALITY' in globals() else 100
    THUMBNAIL_SHARPENING = THUMBNAIL_SHARPENING if 'THUMBNAIL_SHARPENING' in globals() else False
    PRESERVE_ICC_PROFILE = PRESERVE_ICC_PROFILE if 'PRESERVE_ICC_PROFILE' in globals() else True
    
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
        """Create optimized WebP version of the image with maximum quality preservation, AWS compatibility, and memory optimization"""
        try:
            with Image.open(original_path) as img:
                # Get original file size for comparison
                original_size = os.path.getsize(original_path)
                
                # MEMORY OPTIMIZATION: Resize large images before processing
                max_dimension = 3000  # Reasonable limit for web use
                if img.width > max_dimension or img.height > max_dimension:
                    # Calculate new dimensions maintaining aspect ratio
                    if img.width > img.height:
                        new_width = max_dimension
                        new_height = int((max_dimension * img.height) / img.width)
                    else:
                        new_height = max_dimension
                        new_width = int((max_dimension * img.width) / img.height)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"Resized large image from {original_path} to {new_width}x{new_height}")
                
                # Preserve original image data and metadata
                original_img = img.copy()
                
                # Handle different color modes properly
                if img.mode in ('RGBA', 'LA'):
                    # For images with alpha channel, preserve transparency if possible
                    if cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS:
                        # Lossless WebP supports alpha channel
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        # Keep RGBA for lossless WebP
                    else:
                        # For quality-based WebP, create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1])
                        img = background
                elif img.mode == 'P':
                    # Handle palette images properly
                    if img.info.get('transparency') is not None:
                        # Palette image with transparency
                        img = img.convert('RGBA')
                        if not (cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS):
                            # Create white background for quality-based WebP
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        # Palette image without transparency
                        img = img.convert('RGB')
                elif img.mode in ('L', 'LA'):
                    # Grayscale images
                    if img.mode == 'LA':
                        img = img.convert('RGBA')
                        if not (cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode not in ('RGB', 'RGBA'):
                    # Convert any other modes to RGB
                    img = img.convert('RGB')
                
                # PERFORMANCE: Use faster quality for development
                webp_quality = cls.WEBP_QUALITY if cls.PRODUCTION_MODE else min(cls.WEBP_QUALITY, 85)
                webp_method = cls.WEBP_METHOD if cls.PRODUCTION_MODE else min(cls.WEBP_METHOD, 4)
                
                # Save as WebP with optimal settings and AWS compatibility
                if cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS:
                    # Lossless WebP for maximum quality preservation
                    save_kwargs = {
                        'format': 'WEBP',
                        'lossless': True,
                        'method': webp_method,
                        'optimize': True
                    }
                    
                    # Add advanced quality settings if available and safe
                    if cls.AWS_SAFE_MODE:
                        try:
                            if cls.ALPHA_QUALITY:
                                save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                        except:
                            pass  # Skip if not supported
                    else:
                        # Try advanced features if not in AWS safe mode
                        try:
                            if cls.ALPHA_QUALITY:
                                save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                            if cls.USE_SHARP_YUVA:
                                save_kwargs['sharp_yuva'] = True
                        except:
                            pass  # Ignore if PIL version doesn't support these options
                    
                    # Preserve metadata if possible and enabled
                    if cls.PRESERVE_METADATA and hasattr(original_img, 'info') and original_img.info:
                        try:
                            if original_img.info.get('exif'):
                                save_kwargs['exif'] = original_img.info.get('exif', b'')
                            if cls.PRESERVE_ICC_PROFILE and original_img.info.get('icc_profile'):
                                save_kwargs['icc_profile'] = original_img.info.get('icc_profile', b'')
                        except:
                            pass  # Ignore metadata errors
                else:
                    # High quality WebP
                    save_kwargs = {
                        'format': 'WEBP',
                        'quality': webp_quality,
                        'method': webp_method,
                        'optimize': True
                    }
                    
                    # Add advanced quality settings if available and safe
                    if cls.AWS_SAFE_MODE:
                        try:
                            if cls.ALPHA_QUALITY:
                                save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                        except:
                            pass  # Skip if not supported
                    else:
                        # Try advanced features if not in AWS safe mode
                        try:
                            if cls.ALPHA_QUALITY:
                                save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                            if cls.USE_SHARP_YUVA:
                                save_kwargs['sharp_yuva'] = True
                        except:
                            pass  # Ignore if PIL version doesn't support these options
                
                # Save with error handling and fallbacks
                try:
                    img.save(webp_path, **save_kwargs)
                    
                    # Check file size improvement
                    webp_size = os.path.getsize(webp_path)
                    compression_ratio = (1 - webp_size / original_size) * 100
                    logger.info(f"WebP created: {os.path.basename(webp_path)} - {compression_ratio:.1f}% smaller")
                    
                except Exception as save_error:
                    logger.warning(f"Advanced WebP save failed, trying basic save: {str(save_error)}")
                    # Fallback to basic save
                    fallback_kwargs = {
                        'format': 'WEBP',
                        'quality': webp_quality if not cls.WEBP_LOSSLESS else None,
                        'lossless': cls.WEBP_LOSSLESS,
                        'method': min(webp_method, 4)  # Use safer method
                    }
                    if cls.WEBP_LOSSLESS:
                        fallback_kwargs.pop('quality', None)
                    else:
                        fallback_kwargs.pop('lossless', None)
                    
                    img.save(webp_path, **fallback_kwargs)
                
                # Set proper permissions
                os.chmod(webp_path, 0o644)
                
        except Exception as e:
            logger.error(f"Error creating WebP for {original_path}: {str(e)}")
            raise
    
    @classmethod
    def _create_thumbnails(cls, original_path, output_folder, base_name, image_type):
        """Create thumbnails in different sizes with maximum quality preservation"""
        try:
            with Image.open(original_path) as img:
                # Preserve original image data and metadata
                original_img = img.copy()
                
                # Handle different color modes properly (same as main image processing)
                if img.mode in ('RGBA', 'LA'):
                    # For images with alpha channel, preserve transparency if possible
                    if cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS:
                        # Lossless WebP supports alpha channel
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        # Keep RGBA for lossless WebP
                    else:
                        # For quality-based WebP, create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1])
                        img = background
                elif img.mode == 'P':
                    # Handle palette images properly
                    if img.info.get('transparency') is not None:
                        # Palette image with transparency
                        img = img.convert('RGBA')
                        if not (cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS):
                            # Create white background for quality-based WebP
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        # Palette image without transparency
                        img = img.convert('RGB')
                elif img.mode in ('L', 'LA'):
                    # Grayscale images
                    if img.mode == 'LA':
                        img = img.convert('RGBA')
                        if not (cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode not in ('RGB', 'RGBA'):
                    # Convert any other modes to RGB
                    img = img.convert('RGB')
                
                # Create thumbnails for each size
                for size_name, dimensions in cls.THUMBNAIL_SIZES.items():
                    if dimensions is None:  # Skip original size
                        continue
                    
                    # Create high-quality thumbnail
                    if cls.THUMBNAIL_METHOD == 'fit':
                        # Crop to exact size using best quality method
                        thumbnail = ImageOps.fit(
                            img, 
                            dimensions, 
                            method=Image.Resampling.LANCZOS,
                            centering=(0.5, 0.5)
                        )
                    elif cls.THUMBNAIL_METHOD == 'padded':
                        # Method with padding to maintain dimensions
                        thumbnail = cls._create_high_quality_padded_thumbnail(img, dimensions)
                    else:
                        # Default method - preserves aspect ratio with highest quality
                        # Use resize instead of thumbnail for better quality control
                        img_ratio = img.width / img.height
                        target_ratio = dimensions[0] / dimensions[1]
                        
                        if img_ratio > target_ratio:
                            # Image is wider - scale by width
                            new_width = dimensions[0]
                            new_height = int(dimensions[0] / img_ratio)
                        else:
                            # Image is taller - scale by height
                            new_height = dimensions[1]
                            new_width = int(dimensions[1] * img_ratio)
                        
                        # Use highest quality resampling
                        thumbnail = img.resize(
                            (new_width, new_height), 
                            Image.Resampling.LANCZOS
                        )
                    
                    # Apply sharpening if enabled and safe
                    if cls.THUMBNAIL_SHARPENING and not cls.AWS_SAFE_MODE and size_name in ['small', 'medium']:  # Only sharpen smaller thumbnails
                        try:
                            from PIL import ImageFilter
                            # Apply subtle sharpening
                            thumbnail = thumbnail.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=0))
                        except Exception as sharp_error:
                            logger.warning(f"Thumbnail sharpening failed, skipping: {str(sharp_error)}")
                            pass  # Ignore sharpening errors
                    
                    # Save as WebP with optimal settings
                    webp_filename = f"{base_name}_{size_name}.webp"
                    webp_path = os.path.join(output_folder, webp_filename)
                    
                    if cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS:
                        # Lossless WebP for maximum quality preservation
                        save_kwargs = {
                            'format': 'WEBP',
                            'lossless': True,
                            'method': cls.WEBP_METHOD,
                            'optimize': True
                        }
                        
                        # Add advanced quality settings if available and safe
                        if cls.AWS_SAFE_MODE:
                            try:
                                if cls.ALPHA_QUALITY:
                                    save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                            except:
                                pass  # Skip if not supported
                        else:
                            # Try advanced features if not in AWS safe mode
                            try:
                                if cls.ALPHA_QUALITY:
                                    save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                                if cls.USE_SHARP_YUVA:
                                    save_kwargs['sharp_yuva'] = True
                            except:
                                pass  # Ignore if PIL version doesn't support these options
                        
                        # Preserve metadata if possible and enabled
                        if cls.PRESERVE_METADATA and hasattr(original_img, 'info') and original_img.info:
                            try:
                                if original_img.info.get('exif'):
                                    save_kwargs['exif'] = original_img.info.get('exif', b'')
                                if cls.PRESERVE_ICC_PROFILE and original_img.info.get('icc_profile'):
                                    save_kwargs['icc_profile'] = original_img.info.get('icc_profile', b'')
                            except:
                                pass  # Ignore metadata errors
                    else:
                        # High quality WebP
                        save_kwargs = {
                            'format': 'WEBP',
                            'quality': cls.WEBP_QUALITY,
                            'method': cls.WEBP_METHOD,
                            'optimize': True
                        }
                        
                        # Add advanced quality settings if available and safe
                        if cls.AWS_SAFE_MODE:
                            try:
                                if cls.ALPHA_QUALITY:
                                    save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                            except:
                                pass  # Skip if not supported
                        else:
                            # Try advanced features if not in AWS safe mode
                            try:
                                if cls.ALPHA_QUALITY:
                                    save_kwargs['alpha_quality'] = cls.ALPHA_QUALITY
                                if cls.USE_SHARP_YUVA:
                                    save_kwargs['sharp_yuva'] = True
                            except:
                                pass  # Ignore if PIL version doesn't support these options
                    
                    # Save with error handling and fallbacks
                    try:
                        thumbnail.save(webp_path, **save_kwargs)
                    except Exception as save_error:
                        logger.warning(f"Advanced WebP thumbnail save failed, trying basic save: {str(save_error)}")
                        # Fallback to basic save
                        fallback_kwargs = {
                            'format': 'WEBP',
                            'quality': cls.WEBP_QUALITY if not cls.WEBP_LOSSLESS else None,
                            'lossless': cls.WEBP_LOSSLESS,
                            'method': min(cls.WEBP_METHOD, 4)  # Use safer method
                        }
                        if cls.WEBP_LOSSLESS:
                            fallback_kwargs.pop('quality', None)
                        else:
                            fallback_kwargs.pop('lossless', None)
                        
                        thumbnail.save(webp_path, **fallback_kwargs)
                    
                    # Set proper permissions
                    os.chmod(webp_path, 0o644)
                    
        except Exception as e:
            logger.error(f"Error creating thumbnails for {original_path}: {str(e)}")
            raise
    

    
    @classmethod
    def _create_high_quality_padded_thumbnail(cls, img, dimensions):
        """Create a single padded thumbnail with high quality and maximum preservation"""
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
                    
                    # Save as WebP with lossless encoding for maximum quality
                    webp_filename = f"{base_name}_{size_name}_padded.webp"
                    webp_path = os.path.join(output_folder, webp_filename)
                    
                    if cls.PRODUCTION_MODE and cls.WEBP_LOSSLESS:
                        # Use lossless WebP for maximum quality preservation (production)
                        final_thumbnail.save(webp_path, 'WEBP', lossless=True, method=cls.WEBP_METHOD, optimize=True)
                    else:
                        # Use quality-based WebP (development mode or fallback)
                        quality = cls.WEBP_QUALITY
                        final_thumbnail.save(webp_path, 'WEBP', quality=quality, method=cls.WEBP_METHOD, optimize=True)
                    
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
