"""
Consolidated Image Optimizer - Enhanced version combining all optimization features
Handles WebP conversion, multiple formats, intelligent sizing, and storage management
"""
import os
import io
import logging
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
import hashlib
from typing import Optional, Dict, Tuple, Union

logger = logging.getLogger(__name__)

class ConsolidatedImageOptimizer:
    """
    Enhanced image optimizer that handles multiple formats, intelligent sizing,
    and provides format choice based on content and requirements
    """
    
    def __init__(self):
        self.settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
        self.thumbnail_sizes = self.settings.get('THUMBNAIL_SIZES', {
            'xs': (150, 150),
            'sm': (300, 300),
            'md': (600, 600),
            'lg': (800, 800),
            'xl': (1200, 1200),
            'full': (1920, 1080),
        })
        self.webp_quality = self.settings.get('WEBP_QUALITY', 98)
        self.jpeg_quality = self.settings.get('JPEG_QUALITY', 95)
        self.png_quality = self.settings.get('PNG_QUALITY', 9)
        self.delete_original = self.settings.get('DELETE_ORIGINAL', False)  # Changed to False for safety
        self.compression_method = self.settings.get('COMPRESSION_METHOD', 6)
        self.lossless_threshold = self.settings.get('LOSSLESS_THRESHOLD', 0.95)
        self.max_width = self.settings.get('MAX_WIDTH', 2560)
        self.max_height = self.settings.get('MAX_HEIGHT', 1440)
        self.enable_avif = self.settings.get('ENABLE_AVIF', False)
        
    def optimize_and_convert_image(
        self, 
        image_field, 
        instance, 
        target_format: str = 'auto',
        quality: str = 'high',
        max_dimensions: Optional[Tuple[int, int]] = None
    ) -> Optional[File]:
        """
        Main function to optimize and convert uploaded image
        """
        if not image_field or not image_field.name:
            return None
        
        try:
            logger.info(f"Starting optimization for: {image_field.name}")
            
            # Get original image path and extension
            original_path = image_field.name
            original_ext = os.path.splitext(original_path)[1].lower()
            
            # Determine target format intelligently
            if target_format == 'auto':
                target_format = self._choose_best_format(original_ext, quality)
            
            # Skip if already in target format and no resizing needed
            if (original_ext == f'.{target_format.lower()}' and 
                not max_dimensions and 
                not self._needs_resizing(image_field)):
                logger.info(f"Image {original_path} is already optimized")
                return image_field
            
            # Create optimized version
            optimized_path = self._create_optimized_version(
                image_field, 
                target_format, 
                quality, 
                max_dimensions
            )
            
            if optimized_path:
                # Update the image field to use optimized version
                self._update_image_field(image_field, optimized_path, instance)
                
                # Generate thumbnails if enabled
                if self.settings.get('GENERATE_THUMBNAILS', True):
                    self._generate_thumbnails(optimized_path, target_format, quality)
                
                # Delete original file if configured (and different from optimized)
                if (self.delete_original and 
                    original_path != optimized_path and 
                    original_ext != f'.{target_format.lower()}'):
                    self._delete_original_file(original_path)
                
                logger.info(f"Successfully optimized {original_path} to {target_format}: {optimized_path}")
                return image_field
            
        except Exception as e:
            logger.error(f"Error optimizing image {image_field.name}: {e}")
            return image_field
    
    def _choose_best_format(self, original_ext: str, quality: str) -> str:
        """
        Intelligently choose the best output format based on content and quality
        """
        # For high quality, prefer lossless formats
        if quality in ['ultra', 'high']:
            if original_ext in ['.png', '.gif']:
                return 'PNG'  # Keep PNG for transparency
            elif original_ext in ['.jpg', '.jpeg']:
                return 'WEBP'  # WebP for better compression
            else:
                return 'WEBP'
        
        # For medium quality, use WebP for better compression
        elif quality == 'medium':
            return 'WEBP'
        
        # For low quality, use JPEG for maximum compatibility
        else:
            return 'JPEG'
    
    def _needs_resizing(self, image_field) -> bool:
        """Check if image needs resizing"""
        try:
            with Image.open(image_field) as img:
                return img.width > self.max_width or img.height > self.max_height
        except:
            return False
    
    def _create_optimized_version(
        self, 
        image_field, 
        target_format: str, 
        quality: str, 
        max_dimensions: Optional[Tuple[int, int]] = None
    ) -> Optional[str]:
        """Create optimized version of the image"""
        try:
            with Image.open(image_field) as img:
                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Convert RGBA to RGB for JPEG/WebP if needed
                if target_format in ['JPEG', 'WEBP'] and img.mode in ('RGBA', 'LA', 'P'):
                    img = self._convert_to_rgb(img)
                
                # Resize if needed
                if max_dimensions or self._needs_resizing(image_field):
                    img = self._resize_image(img, max_dimensions or (self.max_width, self.max_height))
                
                # Save optimized image
                output = io.BytesIO()
                save_kwargs = self._get_save_kwargs(target_format, quality)
                
                img.save(output, **save_kwargs)
                output.seek(0)
                
                # Generate new filename
                new_filename = self._generate_optimized_filename(
                    image_field.name, 
                    target_format
                )
                
                # Save to storage
                content_file = ContentFile(output.getvalue())
                default_storage.save(new_filename, content_file)
                
                return new_filename
                
        except Exception as e:
            logger.error(f"Error creating optimized version: {e}")
            return None
    
    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert image to RGB mode"""
        if img.mode == 'P':
            img = img.convert('RGBA')
        
        if img.mode == 'RGBA':
            # Create white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        
        return img.convert('RGB')
    
    def _resize_image(self, img: Image.Image, max_dimensions: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        max_width, max_height = max_dimensions
        
        if img.width <= max_width and img.height <= max_height:
            return img
        
        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_width / img.width, max_height / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        
        # Use high-quality resampling
        resample = Image.Resampling.LANCZOS if hasattr(Image.Resampling, 'LANCZOS') else Image.LANCZOS
        
        return img.resize((new_width, new_height), resample)
    
    def _get_save_kwargs(self, format: str, quality: str) -> Dict:
        """Get save parameters based on format and quality"""
        base_kwargs = {'format': format, 'optimize': True}
        
        if format == 'JPEG':
            quality_value = self._get_quality_value(quality, self.jpeg_quality)
            base_kwargs.update({
                'quality': quality_value,
                'progressive': True,
                'subsampling': 0
            })
        elif format == 'PNG':
            quality_value = self._get_quality_value(quality, self.png_quality)
            base_kwargs.update({
                'compress_level': quality_value,
                'optimize': True
            })
        elif format == 'WEBP':
            quality_value = self._get_quality_value(quality, self.webp_quality)
            base_kwargs.update({
                'quality': quality_value,
                'method': self.compression_method,
                'lossless': quality_value >= int(self.lossless_threshold * 100)
            })
        
        return base_kwargs
    
    def _get_quality_value(self, quality: str, default: int) -> int:
        """Convert quality string to numeric value"""
        quality_map = {
            'low': 60,
            'medium': 80,
            'high': 90,
            'ultra': 98
        }
        return quality_map.get(quality, default)
    
    def _generate_optimized_filename(self, original_path: str, format: str) -> str:
        """Generate filename for optimized image"""
        base_name = os.path.splitext(original_path)[0]
        return f"{base_name}_optimized.{format.lower()}"
    
    def _update_image_field(self, image_field, new_path: str, instance) -> None:
        """Update the image field to use the optimized version"""
        try:
            # Open the new file and update the field
            with default_storage.open(new_path, 'rb') as f:
                image_field.save(
                    os.path.basename(new_path),
                    File(f),
                    save=False
                )
        except Exception as e:
            logger.error(f"Error updating image field: {e}")
    
    def _generate_thumbnails(self, image_path: str, format: str, quality: str) -> None:
        """Generate thumbnails for different sizes"""
        try:
            with default_storage.open(image_path, 'rb') as f:
                with Image.open(f) as img:
                    for size_name, (width, height) in self.thumbnail_sizes.items():
                        self._create_thumbnail(img, image_path, size_name, width, height, format, quality)
        except Exception as e:
            logger.error(f"Error generating thumbnails: {e}")
    
    def _create_thumbnail(
        self, 
        img: Image.Image, 
        original_path: str, 
        size_name: str, 
        width: int, 
        height: int, 
        format: str, 
        quality: str
    ) -> None:
        """Create a single thumbnail"""
        try:
            # Resize image
            resized = img.copy()
            resized.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output = io.BytesIO()
            save_kwargs = self._get_save_kwargs(format, quality)
            resized.save(output, **save_kwargs)
            output.seek(0)
            
            # Generate thumbnail filename
            base_name = os.path.splitext(original_path)[0]
            thumbnail_filename = f"{base_name}_{size_name}.{format.lower()}"
            
            # Save to storage
            content_file = ContentFile(output.getvalue())
            default_storage.save(thumbnail_filename, content_file)
            
        except Exception as e:
            logger.error(f"Error creating thumbnail {size_name}: {e}")
    
    def _delete_original_file(self, file_path: str) -> None:
        """Delete original file if it exists"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                logger.info(f"Deleted original file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting original file {file_path}: {e}")


# Convenience functions for backward compatibility
def optimize_uploaded_image(image_field, instance, **kwargs):
    """Main function to optimize uploaded images"""
    if not image_field or not getattr(settings, 'IMAGE_OPTIMIZATION', {}).get('OPTIMIZE_ON_UPLOAD', True):
        return None
    
    try:
        optimizer = ConsolidatedImageOptimizer()
        result = optimizer.optimize_and_convert_image(image_field, instance, **kwargs)
        
        if result:
            logger.info(f"Successfully optimized and converted image: {image_field.name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in consolidated image optimization: {e}")
        return None


def get_responsive_image_urls(image_path: str, sizes: Optional[list] = None) -> Dict[str, str]:
    """Get responsive image URLs for different screen sizes"""
    if not image_path:
        return {}
    
    if sizes is None:
        sizes = ['xs', 'sm', 'md', 'lg', 'xl', 'full']
    
    urls = {}
    base_name = os.path.splitext(image_path)[0]
    
    for size in sizes:
        # Check if thumbnail exists
        thumbnail_path = f"{base_name}_{size}.webp"
        if default_storage.exists(thumbnail_path):
            urls[size] = f"/media/{thumbnail_path}"
        else:
            # Fallback to original
            urls[size] = f"/media/{image_path}"
    
    return urls


def optimize_image(image_field, max_width=None, max_height=None, quality=None, format=None):
    """
    Backward compatibility function for optimize_image
    """
    if not image_field:
        return None
    
    try:
        optimizer = ConsolidatedImageOptimizer()
        
        # Set parameters
        if max_width and max_height:
            max_dimensions = (max_width, max_height)
        else:
            max_dimensions = None
        
        if quality is None:
            quality = 'high'
        
        if format is None:
            format = 'auto'
        
        # Create a dummy instance for compatibility
        class DummyInstance:
            def __init__(self):
                pass
        
        result = optimizer.optimize_and_convert_image(
            image_field, 
            DummyInstance(), 
            target_format=format,
            quality=quality,
            max_dimensions=max_dimensions
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in optimize_image: {e}")
        return None


def should_optimize_image(image_field, max_size_mb: float = 2, max_width: int = 1920, max_height: int = 1080) -> bool:
    """Check if image should be optimized"""
    if not image_field:
        return False
    
    try:
        # Check file size
        if hasattr(image_field, 'size') and image_field.size > max_size_mb * 1024 * 1024:
            return True
        
        # Check dimensions
        with Image.open(image_field) as img:
            if img.width > max_width or img.height > max_height:
                return True
        
        # Check format
        if hasattr(image_field, 'name'):
            ext = os.path.splitext(image_field.name)[1].lower()
            if ext not in ['.webp', '.avif']:
                return True
        
        return False
        
    except Exception:
        return True
