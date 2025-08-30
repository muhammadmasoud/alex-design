"""
Image Optimizer Configuration
Easy configuration for switching between production and development modes
AWS-compatible version with robust fallbacks
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
DEVELOPMENT_WEBP_QUALITY = 95  # Very high quality for development
DEVELOPMENT_JPEG_QUALITY = 95  # Very high quality for development
DEVELOPMENT_WEBP_LOSSLESS = False  # Disable lossless for speed
DEVELOPMENT_WEBP_METHOD = 4  # Balanced compression method

# Advanced Quality Settings (AWS-compatible)
PRESERVE_METADATA = True  # Preserve EXIF and color profile data
PRESERVE_TRANSPARENCY = True  # Preserve alpha channels when possible
USE_SHARP_YUVA = False  # Disabled for AWS compatibility (may not be supported)
ALPHA_QUALITY = 100  # Quality for alpha channel (WebP only)

# Thumbnail Configuration
THUMBNAIL_METHOD = 'thumbnail'  # 'fit', 'thumbnail', 'padded'
THUMBNAIL_SIZES = {
    'small': (400, 400),      # Increased for better quality
    'medium': (1000, 1000),   # Increased for better quality
    'large': (1600, 1600),    # Increased for better quality
    'original': None           # Keep original size
}

# Resampling Settings
RESAMPLING_FILTER = 'LANCZOS'  # Highest quality resampling filter
THUMBNAIL_SHARPENING = False  # Disabled for AWS compatibility (may cause issues)

# Performance Settings
ENABLE_IMAGE_CACHING = True  # Cache optimized images
PARALLEL_PROCESSING = False  # Enable parallel processing (may use more memory)
MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB max image size

# Color Space Settings
FORCE_SRGB = False  # Disabled for AWS compatibility
PRESERVE_ICC_PROFILE = True  # Preserve color profiles when possible

# AWS Compatibility Settings
AWS_SAFE_MODE = True  # Enable AWS-safe mode with fallbacks
SKIP_ADVANCED_FEATURES = True  # Skip features that might not work on AWS
