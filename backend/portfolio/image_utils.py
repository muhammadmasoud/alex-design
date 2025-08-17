"""
Image optimization utilities for production
"""
import os
from PIL import Image, ImageOps
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io


def optimize_image(image_field, max_width=1920, max_height=1080, quality=85, format='JPEG'):
    """
    Optimize image for web delivery:
    - Resize to max dimensions while maintaining aspect ratio
    - Compress to reduce file size
    - Convert to optimized format (JPEG for photos, PNG for graphics with transparency)
    """
    if not image_field:
        return
    
    try:
        # Open the image
        image = Image.open(image_field)
        
        # Convert RGBA to RGB for JPEG format to avoid transparency issues
        if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Auto-orient based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Calculate new dimensions while maintaining aspect ratio
        original_width, original_height = image.size
        
        # Only resize if image is larger than max dimensions
        if original_width > max_width or original_height > max_height:
            # Calculate aspect ratios
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            
            # Use the smaller ratio to maintain aspect ratio
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            # Resize using high-quality resampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save optimized image to memory
        output = io.BytesIO()
        
        # Optimize save parameters based on format
        save_kwargs = {'format': format, 'optimize': True}
        
        if format.upper() == 'JPEG':
            save_kwargs.update({
                'quality': quality,
                'progressive': True,  # Progressive JPEG for better perceived loading
            })
        elif format.upper() == 'PNG':
            save_kwargs.update({
                'compress_level': 6,  # Good compression without too much CPU
            })
        elif format.upper() == 'WEBP':
            save_kwargs.update({
                'quality': quality,
                'method': 6,  # Best compression
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
