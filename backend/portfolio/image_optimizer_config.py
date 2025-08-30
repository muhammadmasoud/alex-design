"""
Image Optimizer Configuration
Easy configuration for switching between production and development modes
"""

# Production Mode Configuration
# Set to True for production (0% quality loss, slower processing)
# Set to False for development (faster processing, high quality)
PRODUCTION_MODE = True

# Quality Settings for Production Mode (when PRODUCTION_MODE = True)
PRODUCTION_WEBP_QUALITY = 100  # Maximum quality
PRODUCTION_JPEG_QUALITY = 100  # Maximum quality
PRODUCTION_WEBP_LOSSLESS = True  # Enable true lossless encoding
PRODUCTION_WEBP_METHOD = 6  # Slowest but highest quality compression method

# Quality Settings for Development Mode (when PRODUCTION_MODE = False)
DEVELOPMENT_WEBP_QUALITY = 95  # Very high quality for development (increased from 85)
DEVELOPMENT_JPEG_QUALITY = 95  # Very high quality for development (increased from 88)
DEVELOPMENT_WEBP_LOSSLESS = False  # Disable lossless for speed
DEVELOPMENT_WEBP_METHOD = 4  # Balanced compression method

# Advanced Quality Settings
PRESERVE_METADATA = True  # Preserve EXIF and color profile data
PRESERVE_TRANSPARENCY = True  # Preserve alpha channels when possible
USE_SHARP_YUVA = True  # Use sharp YUV conversion (better quality)
ALPHA_QUALITY = 100  # Quality for alpha channel (WebP only)

# Thumbnail Configuration
THUMBNAIL_METHOD = 'thumbnail'  # 'fit', 'thumbnail', 'padded'
THUMBNAIL_SIZES = {
    'small': (400, 400),      # Increased for better quality (was 300x300)
    'medium': (1000, 1000),   # Increased for better quality (was 800x800)
    'large': (1600, 1600),    # Increased for better quality (was 1200x1200)
    'original': None           # Keep original size
}

# Resampling Settings
RESAMPLING_FILTER = 'LANCZOS'  # Highest quality resampling filter
THUMBNAIL_SHARPENING = True  # Apply subtle sharpening to thumbnails

# Performance Settings
ENABLE_IMAGE_CACHING = True  # Cache optimized images
PARALLEL_PROCESSING = False  # Enable parallel processing (may use more memory)
MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB max image size (increased from 50MB)

# Color Space Settings
FORCE_SRGB = True  # Convert all images to sRGB color space for web consistency
PRESERVE_ICC_PROFILE = True  # Preserve color profiles when possible
