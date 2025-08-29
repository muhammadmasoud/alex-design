"""
Production-ready image optimization system
Automatically generates multiple sizes and formats for optimal performance
"""
import os
import io
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

class ImageOptimizer:
    """
    Handles automatic image optimization and thumbnail generation
    """
    
    # Standard sizes for different use cases
    THUMBNAIL_SIZES = {
        'xs': (150, 150),      # Grid thumbnails
        'sm': (300, 300),      # Small previews
        'md': (600, 600),      # Medium previews
        'lg': (800, 800),      # Large previews
        'xl': (1200, 1200),    # High-res previews
    }
    
    # Quality settings for different formats
    QUALITY_SETTINGS = {
        'JPEG': {
            'low': 80,      # Increased from 60
            'medium': 90,   # Increased from 80
            'high': 95,     # Increased from 90
            'ultra': 98     # Increased from 95
        },
        'WEBP': {
            'low': 85,      # Increased from 70
            'medium': 92,   # Increased from 85
            'high': 98,     # Increased from 95
            'ultra': 100    # Keep at 100
        }
    }
    
    @classmethod
    def optimize_image(cls, image_path, output_format='JPEG', quality='high', max_size=None):
        """
        Optimize a single image with specified settings
        """
        try:
            if not default_storage.exists(image_path):
                logger.warning(f"Image not found: {image_path}")
                return None
            
            with default_storage.open(image_path, 'rb') as img_file:
                with Image.open(img_file) as img:
                    # Convert to RGB if needed
                    if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                        img = cls._convert_to_rgb(img)
                    
                    # Resize if max_size specified
                    if max_size:
                        img = cls._resize_image(img, max_size)
                    
                    # Get quality setting
                    quality_value = cls.QUALITY_SETTINGS.get(output_format, {}).get(quality, 95)
                    
                    # Prepare output
                    output = io.BytesIO()
                    
                    # Save with optimization
                    save_kwargs = {
                        'format': output_format,
                        'optimize': True,
                        'quality': quality_value
                    }
                    
                    if output_format == 'JPEG':
                        save_kwargs.update({
                            'progressive': True,
                            'subsampling': 0
                        })
                    elif output_format == 'WEBP':
                        save_kwargs.update({
                            'method': 6,
                            'lossless': quality == 'ultra'
                        })
                    
                    img.save(output, **save_kwargs)
                    output.seek(0)
                    
                    return output
                    
        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {e}")
            return None
    
    @classmethod
    def generate_thumbnails(cls, image_path, sizes=None):
        """
        Generate multiple thumbnail sizes for an image
        """
        if sizes is None:
            sizes = cls.THUMBNAIL_SIZES
        
        thumbnails = {}
        
        try:
            if not default_storage.exists(image_path):
                logger.warning(f"Image not found for thumbnails: {image_path}")
                return thumbnails
            
            with default_storage.open(image_path, 'rb') as img_file:
                with Image.open(img_file) as img:
                    for size_name, (width, height) in sizes.items():
                        try:
                            thumbnail = cls._create_thumbnail(img, width, height)
                            if thumbnail:
                                thumbnails[size_name] = thumbnail
                        except Exception as e:
                            logger.error(f"Error creating thumbnail {size_name} for {image_path}: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error generating thumbnails for {image_path}: {e}")
        
        return thumbnails
    
    @classmethod
    def save_optimized_versions(cls, image_path, output_dir=None):
        """
        Save multiple optimized versions of an image
        """
        if output_dir is None:
            # Create output directory based on original path
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = os.path.join(os.path.dirname(image_path), 'optimized', base_name)
        
        saved_files = {}
        
        try:
            # Generate different quality versions
            for quality in ['low', 'medium', 'high']:
                # JPEG version
                jpeg_output = cls.optimize_image(image_path, 'JPEG', quality)
                if jpeg_output:
                    jpeg_filename = f"{base_name}_q{cls.QUALITY_SETTINGS['JPEG'][quality]}.jpg"
                    jpeg_path = os.path.join(output_dir, jpeg_filename)
                    
                    if cls._save_file(jpeg_output, jpeg_path):
                        saved_files[f'jpeg_{quality}'] = jpeg_path
                
                # WebP version
                webp_output = cls.optimize_image(image_path, 'WEBP', quality)
                if webp_output:
                    webp_filename = f"{base_name}_q{cls.QUALITY_SETTINGS['WEBP'][quality]}.webp"
                    webp_path = os.path.join(output_dir, webp_filename)
                    
                    if cls._save_file(webp_output, webp_path):
                        saved_files[f'webp_{quality}'] = webp_path
            
            # Generate thumbnails
            thumbnails = cls.generate_thumbnails(image_path)
            for size_name, thumbnail_data in thumbnails.items():
                thumbnail_filename = f"{base_name}_{size_name}.jpg"
                thumbnail_path = os.path.join(output_dir, thumbnail_filename)
                
                if cls._save_file(thumbnail_data, thumbnail_path):
                    saved_files[f'thumbnail_{size_name}'] = thumbnail_path
                    
        except Exception as e:
            logger.error(f"Error saving optimized versions for {image_path}: {e}")
        
        return saved_files
    
    @classmethod
    def _convert_to_rgb(cls, img):
        """Convert image to RGB mode"""
        if img.mode == 'P':
            img = img.convert('RGBA')
        
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        elif img.mode == 'LA':
            # Convert grayscale with alpha to RGB
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img.convert('RGB'), mask=img.split()[-1])
            return background
        
        return img.convert('RGB')
    
    @classmethod
    def _resize_image(cls, img, max_size):
        """Resize image maintaining aspect ratio"""
        if isinstance(max_size, (int, float)):
            max_size = (max_size, max_size)
        
        # Calculate new size maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    
    @classmethod
    def _create_thumbnail(cls, img, width, height):
        """Create thumbnail with specified dimensions"""
        try:
            # Create copy to avoid modifying original
            thumb = img.copy()
            
            # Resize maintaining aspect ratio
            thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if thumb.mode in ('RGBA', 'LA', 'P'):
                thumb = cls._convert_to_rgb(thumb)
            
            # Prepare output
            output = io.BytesIO()
            thumb.save(output, format='JPEG', quality=95, optimize=True, progressive=True)
            output.seek(0)
            
            return output
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return None
    
    @classmethod
    def _save_file(cls, file_data, file_path):
        """Save file data to storage"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data.getvalue())
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    @classmethod
    def get_optimized_url(cls, original_path, size='md', format='webp', quality='high'):
        """
        Generate URL for optimized image version
        """
        if not original_path:
            return None
        
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        dir_name = os.path.dirname(original_path)
        
        if format == 'webp':
            quality_value = cls.QUALITY_SETTINGS['WEBP'].get(quality, 85)
            filename = f"{base_name}_q{quality_value}.webp"
        else:
            quality_value = cls.QUALITY_SETTINGS['JPEG'].get(quality, 85)
            filename = f"{base_name}_q{quality_value}.jpg"
        
        if size != 'original':
            filename = f"{base_name}_{size}.jpg"
        
        optimized_path = os.path.join(dir_name, 'optimized', base_name, filename)
        
        # Check if optimized version exists
        if default_storage.exists(optimized_path):
            return f"/media/{optimized_path}"
        
        # Fallback to original
        return f"/media/{original_path}"


def optimize_uploaded_image(image_field, instance):
    """
    Hook function to automatically optimize images when they're uploaded
    """
    if not image_field:
        return
    
    try:
        image_path = image_field.name
        
        # Generate optimized versions
        optimizer = ImageOptimizer()
        saved_files = optimizer.save_optimized_versions(image_path)
        
        if saved_files:
            logger.info(f"Generated {len(saved_files)} optimized versions for {image_path}")
            
            # Store paths in instance if needed
            if hasattr(instance, 'optimized_versions'):
                instance.optimized_versions = saved_files
        
    except Exception as e:
        logger.error(f"Error optimizing uploaded image: {e}")


def get_responsive_image_urls(image_path, sizes=None):
    """
    Get responsive image URLs for different screen sizes
    """
    if not image_path:
        return {}
    
    if sizes is None:
        sizes = ['xs', 'sm', 'md', 'lg', 'xl']
    
    urls = {}
    
    for size in sizes:
        urls[size] = ImageOptimizer.get_optimized_url(image_path, size)
    
    return urls
