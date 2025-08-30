"""
Advanced Image Optimizer with Next-Gen Format Support
Extends the existing optimizer with AVIF support and progressive JPEG
"""

import os
import logging
from PIL import Image
from .image_optimizer import ImageOptimizer as BaseOptimizer

logger = logging.getLogger(__name__)

class AdvancedImageOptimizer(BaseOptimizer):
    """
    Advanced optimizer with next-generation format support
    """
    
    # Modern format support
    ENABLE_AVIF = True  # Enable AVIF format (smaller than WebP)
    ENABLE_PROGRESSIVE_JPEG = True  # Enable progressive JPEG as fallback
    
    @classmethod
    def _create_modern_formats(cls, original_path, output_folder, base_name, image_type):
        """Create modern image formats (AVIF, Progressive JPEG)"""
        try:
            with Image.open(original_path) as img:
                # Prepare image (same preprocessing as WebP)
                if img.mode in ('RGBA', 'LA'):
                    if not cls.WEBP_LOSSLESS:
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1])
                        img = background
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                # Create AVIF version (smaller than WebP)
                if cls.ENABLE_AVIF:
                    try:
                        avif_path = os.path.join(output_folder, f"{base_name}.avif")
                        
                        # AVIF settings for maximum quality
                        avif_kwargs = {
                            'format': 'AVIF',
                            'quality': 100 if cls.PRODUCTION_MODE else 95,
                            'speed': 1 if cls.PRODUCTION_MODE else 4,  # Slower = better compression
                        }
                        
                        img.save(avif_path, **avif_kwargs)
                        os.chmod(avif_path, 0o644)
                        
                        # Check file size
                        original_size = os.path.getsize(original_path)
                        avif_size = os.path.getsize(avif_path)
                        compression_ratio = (1 - avif_size / original_size) * 100
                        logger.info(f"AVIF created: {os.path.basename(avif_path)} - {compression_ratio:.1f}% smaller")
                        
                    except Exception as avif_error:
                        logger.warning(f"AVIF creation failed (not supported): {str(avif_error)}")
                
                # Create Progressive JPEG fallback
                if cls.ENABLE_PROGRESSIVE_JPEG:
                    try:
                        jpeg_path = os.path.join(output_folder, f"{base_name}_progressive.jpg")
                        
                        # Convert to RGB if needed
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Progressive JPEG settings
                        jpeg_kwargs = {
                            'format': 'JPEG',
                            'quality': cls.JPEG_QUALITY,
                            'progressive': True,
                            'optimize': True,
                        }
                        
                        img.save(jpeg_path, **jpeg_kwargs)
                        os.chmod(jpeg_path, 0o644)
                        
                        logger.info(f"Progressive JPEG created: {os.path.basename(jpeg_path)}")
                        
                    except Exception as jpeg_error:
                        logger.warning(f"Progressive JPEG creation failed: {str(jpeg_error)}")
                        
        except Exception as e:
            logger.error(f"Error creating modern formats for {original_path}: {str(e)}")
    
    @classmethod
    def _create_optimized_webp(cls, original_path, webp_path, image_type):
        """Override to also create modern formats"""
        # Call parent method first
        super()._create_optimized_webp(original_path, webp_path, image_type)
        
        # Create additional modern formats
        output_folder = os.path.dirname(webp_path)
        base_name = os.path.splitext(os.path.basename(webp_path))[0]
        cls._create_modern_formats(original_path, output_folder, base_name, image_type)
