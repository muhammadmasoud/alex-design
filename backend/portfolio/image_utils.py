"""
Image optimization utilities for production
"""
import os
from PIL import Image, ImageOps
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io


def optimize_image(image_field, max_width=None, max_height=None, quality=None, format=None):
    """
    Optimize image for web delivery with high quality preservation:
    - Smart format selection (WebP for better compression, JPEG fallback)
    - Resize to max dimensions while maintaining aspect ratio
    - High-quality compression with minimal quality loss
    - Convert to optimized format based on content
    """
    if not image_field:
        return
    
    # Import here to avoid circular imports
    from django.conf import settings
    
    # Use settings defaults if not provided
    optimization_settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
    if max_width is None:
        max_width = optimization_settings.get('MAX_WIDTH', 2560)
    if max_height is None:
        max_height = optimization_settings.get('MAX_HEIGHT', 1440)
    if quality is None:
        quality = optimization_settings.get('QUALITY', 96)
    
    # Smart format selection
    use_webp = optimization_settings.get('USE_WEBP', True)
    webp_quality = optimization_settings.get('WEBP_QUALITY', 95)
    progressive_jpeg = optimization_settings.get('PROGRESSIVE_JPEG', True)
    
    try:
        # Open the image
        image = Image.open(image_field)
        original_format = image.format
        
        # Auto-orient based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Determine best output format
        if format is None:
            # Smart format selection based on image characteristics
            if use_webp:
                # Use WebP for better compression at high quality
                format = 'WEBP'
                target_quality = webp_quality
            elif image.mode in ('RGBA', 'LA') or (hasattr(image, 'transparency') and image.transparency is not None):
                # Use PNG for images with transparency
                format = 'PNG'
                target_quality = None  # PNG doesn't use quality
            else:
                # Use JPEG for photos
                format = 'JPEG'
                target_quality = quality
        else:
            target_quality = quality
        
        # Convert RGBA to RGB for JPEG format to avoid transparency issues
        if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Calculate new dimensions while maintaining aspect ratio
        original_width, original_height = image.size
        
        # Only resize if image is significantly larger than max dimensions
        # Use a threshold to avoid unnecessary resizing of slightly larger images
        resize_threshold = 1.1
        if (original_width > max_width * resize_threshold or 
            original_height > max_height * resize_threshold):
            
            # Calculate aspect ratios
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            
            # Use the smaller ratio to maintain aspect ratio
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            # Use the highest quality resampling method
            if hasattr(Image.Resampling, 'LANCZOS'):
                resample_method = Image.Resampling.LANCZOS
            else:
                resample_method = Image.LANCZOS
            
            image = image.resize((new_width, new_height), resample_method)
        
        # Save optimized image to memory
        output = io.BytesIO()
        
        # Optimize save parameters based on format
        save_kwargs = {'format': format, 'optimize': True}
        
        if format.upper() == 'JPEG':
            save_kwargs.update({
                'quality': target_quality,
                'progressive': progressive_jpeg,
                'subsampling': 0,  # Disable chroma subsampling for better quality
            })
        elif format.upper() == 'PNG':
            save_kwargs.update({
                'compress_level': 6,  # Good compression without too much CPU
                'optimize': True,
            })
        elif format.upper() == 'WEBP':
            save_kwargs.update({
                'quality': target_quality,
                'method': 6,  # Best compression method
                'lossless': target_quality >= 95,  # Use lossless for very high quality
            })
        
        image.save(output, **save_kwargs)
        output.seek(0)
        
        # Get original filename and change extension if needed
        original_name = image_field.name
        name_parts = original_name.split('.')
        if len(name_parts) > 1:
            name_parts[-1] = format.lower()
            new_name = '.'.join(name_parts)
        else:
            new_name = f"{original_name}.{format.lower()}"
        
        # Create new file
        optimized_file = ContentFile(output.getvalue(), name=new_name)
        
        return optimized_file
        
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None


def create_thumbnail(image_field, size=(300, 300), quality=85):
    """
    Create a thumbnail version of the image
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        image = Image.open(image_field)
        
        # Auto-orient based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Convert RGBA to RGB for JPEG format
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Create thumbnail maintaining aspect ratio
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save thumbnail to memory
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Generate thumbnail filename
        original_name = image_field.name
        name_parts = original_name.split('.')
        if len(name_parts) > 1:
            name_parts[-2] += '_thumb'
            thumb_name = '.'.join(name_parts[:-1]) + '.jpg'
        else:
            thumb_name = f"{original_name}_thumb.jpg"
        
        return ContentFile(output.getvalue(), name=thumb_name)
        
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None


def get_image_info(image_field):
    """
    Get image information for optimization decisions
    """
    if not image_field:
        return None
    
    try:
        image = Image.open(image_field)
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            'size_bytes': image_field.size if hasattr(image_field, 'size') else 0
        }
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None


def should_optimize_image(image_field, max_size_mb=2, max_width=1920, max_height=1080):
    """
    Determine if an image should be optimized based on size and dimensions
    """
    if not image_field:
        return False
    
    try:
        # Check file size
        file_size_mb = image_field.size / (1024 * 1024) if hasattr(image_field, 'size') else 0
        if file_size_mb > max_size_mb:
            return True
        
        # Check dimensions
        info = get_image_info(image_field)
        if info and (info['width'] > max_width or info['height'] > max_height):
            return True
        
        return False
        
    except Exception:
        return False
