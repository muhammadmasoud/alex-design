"""
Enhanced Image Optimizer with WebP conversion and automatic cleanup
Automatically converts all images to WebP format and deletes originals
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

logger = logging.getLogger(__name__)

class EnhancedImageOptimizer:
    """
    Enhanced image optimizer that converts to WebP and manages storage
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
        self.delete_original = self.settings.get('DELETE_ORIGINAL', True)
        self.compression_method = self.settings.get('COMPRESSION_METHOD', 6)
        self.lossless_threshold = self.settings.get('LOSSLESS_THRESHOLD', 0.95)
    
    def optimize_and_convert_image(self, image_field, instance):
        """
        Main function to optimize and convert uploaded image to WebP
        """
        if not image_field or not image_field.name:
            return None
        
        try:
            logger.info(f"Starting optimization for: {image_field.name}")
            
            # Get original image path
            original_path = image_field.name
            original_ext = os.path.splitext(original_path)[1].lower()
            
            # Skip if already WebP
            if original_ext == '.webp':
                logger.info(f"Image {original_path} is already WebP format")
                return image_field
            
            # Create WebP version
            webp_path = self._create_webp_version(image_field)
            
            if webp_path:
                # Update the image field to use WebP version
                self._update_image_field(image_field, webp_path, instance)
                
                # Generate thumbnails if enabled
                if self.settings.get('GENERATE_THUMBNAILS', True):
                    self._generate_thumbnails(webp_path)
                
                # Delete original file if configured
                if self.delete_original and original_ext != '.webp':
                    self._delete_original_file(original_path)
                
                logger.info(f"Successfully converted {original_path} to WebP: {webp_path}")
                return image_field
            
        except Exception as e:
            logger.error(f"Error optimizing image {image_field.name}: {e}")
            return image_field
    
    def _create_webp_version(self, image_field):
        """
        Create WebP version of the uploaded image
        """
        try:
            # Open and process image
            with Image.open(image_field) as img:
                # Convert to RGB if needed (WebP supports RGBA but RGB is more compatible)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if exceeds maximum dimensions
                max_width = self.settings.get('MAX_WIDTH', 2560)
                max_height = self.settings.get('MAX_HEIGHT', 1440)
                
                if img.width > max_width or img.height > max_height:
                    img = self._resize_maintaining_aspect_ratio(img, max_width, max_height)
                
                # Prepare WebP output
                output = io.BytesIO()
                
                # Determine quality and lossless settings
                use_lossless = self.webp_quality >= (self.lossless_threshold * 100)
                
                save_kwargs = {
                    'format': 'WEBP',
                    'quality': self.webp_quality,
                    'method': self.compression_method,
                    'lossless': use_lossless
                }
                
                # Save as WebP
                img.save(output, **save_kwargs)
                output.seek(0)
                
                # Generate new filename
                base_name = os.path.splitext(os.path.basename(image_field.name))[0]
                dir_name = os.path.dirname(image_field.name)
                webp_filename = f"{base_name}_optimized.webp"
                webp_path = os.path.join(dir_name, webp_filename)
                
                # Save WebP file
                if default_storage.exists(webp_path):
                    default_storage.delete(webp_path)
                
                # Save the WebP content
                content_file = ContentFile(output.getvalue())
                default_storage.save(webp_path, content_file)
                
                return webp_path
                
        except Exception as e:
            logger.error(f"Error creating WebP version: {e}")
            return None
    
    def _resize_maintaining_aspect_ratio(self, img, max_width, max_height):
        """
        Resize image maintaining aspect ratio
        """
        # Calculate new dimensions
        width, height = img.size
        aspect_ratio = width / height
        
        if width > max_width:
            width = max_width
            height = int(width / aspect_ratio)
        
        if height > max_height:
            height = max_height
            width = int(height * aspect_ratio)
        
        # Resize using high-quality resampling
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return img
    
    def _update_image_field(self, image_field, webp_path, instance):
        """
        Update the image field to use the new WebP file
        """
        try:
            # Update the field name to point to WebP file
            image_field.name = webp_path
            
            # If this is a model instance, save the change
            if instance and hasattr(instance, 'save'):
                # Temporarily disable the signal to avoid infinite loop
                from django.db.models.signals import pre_save
                pre_save.disconnect(receiver=None, sender=instance.__class__)
                
                try:
                    instance.save(update_fields=[image_field.field.name])
                finally:
                    # Reconnect the signal
                    pre_save.connect(receiver=None, sender=instance.__class__)
            
            logger.info(f"Updated image field to: {webp_path}")
            
        except Exception as e:
            logger.error(f"Error updating image field: {e}")
    
    def _generate_thumbnails(self, webp_path):
        """
        Generate multiple thumbnail sizes for responsive design
        """
        try:
            if not default_storage.exists(webp_path):
                return
            
            with default_storage.open(webp_path, 'rb') as img_file:
                with Image.open(img_file) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Generate thumbnails for each size
                    for size_name, (width, height) in self.thumbnail_sizes.items():
                        self._create_thumbnail(img, webp_path, size_name, width, height)
            
            logger.info(f"Generated thumbnails for: {webp_path}")
            
        except Exception as e:
            logger.error(f"Error generating thumbnails: {e}")
    
    def _create_thumbnail(self, original_img, webp_path, size_name, width, height):
        """
        Create a specific thumbnail size
        """
        try:
            # Create thumbnail
            thumb = original_img.copy()
            thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Prepare output
            output = io.BytesIO()
            thumb.save(output, format='WEBP', quality=self.webp_quality, method=self.compression_method)
            output.seek(0)
            
            # Generate thumbnail path
            base_name = os.path.splitext(os.path.basename(webp_path))[0]
            dir_name = os.path.dirname(webp_path)
            thumb_filename = f"{base_name}_{size_name}.webp"
            
            # Create thumbnails folder in the same directory as the image
            thumb_dir = os.path.join(dir_name, 'thumbnails')
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            
            # Ensure thumbnails directory exists
            try:
                if not os.path.exists(thumb_dir):
                    os.makedirs(thumb_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating thumbnails directory {thumb_dir}: {e}")
            
            # Save thumbnail
            if default_storage.exists(thumb_path):
                default_storage.delete(thumb_path)
            
            content_file = ContentFile(output.getvalue())
            default_storage.save(thumb_path, content_file)
            
            return thumb_path
            
        except Exception as e:
            logger.error(f"Error creating thumbnail {size_name}: {e}")
            return None
    
    def _delete_original_file(self, original_path):
        """
        Delete the original file after successful conversion
        """
        try:
            if default_storage.exists(original_path):
                default_storage.delete(original_path)
                logger.info(f"Deleted original file: {original_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting original file {original_path}: {e}")
        
        return False
    
    def get_optimized_url(self, image_path, size='md'):
        """
        Get URL for optimized image version
        """
        if not image_path:
            return None
        
        # Check if WebP version exists
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        dir_name = os.path.dirname(image_path)
        
        if size == 'original':
            # Return main WebP version
            webp_path = os.path.join(dir_name, f"{base_name}_optimized.webp")
            if default_storage.exists(webp_path):
                return f"/media/{webp_path}"
        else:
            # Return thumbnail version
            thumb_path = os.path.join(dir_name, 'thumbnails', f"{base_name}_{size}.webp")
            if default_storage.exists(thumb_path):
                return f"/media/{thumb_path}"
        
        # Fallback to original
        return f"/media/{image_path}"


def optimize_uploaded_image(image_field, instance):
    """
    Enhanced hook function for automatic WebP conversion and optimization
    """
    if not image_field or not getattr(settings, 'IMAGE_OPTIMIZATION', {}).get('OPTIMIZE_ON_UPLOAD', True):
        return
    
    try:
        optimizer = EnhancedImageOptimizer()
        result = optimizer.optimize_and_convert_image(image_field, instance)
        
        if result:
            logger.info(f"Successfully optimized and converted image: {image_field.name}")
        
    except Exception as e:
        logger.error(f"Error in enhanced image optimization: {e}")


def get_responsive_image_urls(image_path, sizes=None):
    """
    Get responsive image URLs for different screen sizes
    """
    if not image_path:
        return {}
    
    if sizes is None:
        sizes = ['xs', 'sm', 'md', 'lg', 'xl', 'full']
    
    optimizer = EnhancedImageOptimizer()
    urls = {}
    
    for size in sizes:
        urls[size] = optimizer.get_optimized_url(image_path, size)
    
    return urls


def cleanup_orphaned_files():
    """
    Clean up any orphaned files that might exist
    """
    try:
        # This function can be called periodically to clean up
        # any files that might have been left behind
        pass
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")
