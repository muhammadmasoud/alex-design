"""
Image Optimization Configuration
Easy-to-modify settings for controlling image quality and optimization behavior
"""

# Quality Preset Configuration
# Choose one of these presets to control overall image quality
QUALITY_PRESET = 'lossless'  # Options: 'lossless', 'ultra', 'high', 'balanced', 'compressed'

# Quality Preset Details:
# - 'lossless': 100% quality preservation, no quality loss, largest file sizes - Best for portfolios
# - 'ultra': Maximum quality (95-100), larger file sizes - Best for portfolios
# - 'high': High quality (90-95), balanced file sizes - Good balance
# - 'balanced': Good quality (80-90), smaller file sizes - Standard web optimization
# - 'compressed': Lower quality (70-80), smallest file sizes - Maximum compression

# Thumbnail Creation Method
# Choose how thumbnails are created
THUMBNAIL_METHOD = 'thumbnail'  # Options: 'fit', 'thumbnail', 'padded'

# Thumbnail Method Details:
# - 'fit': Crops images to exact dimensions (may lose parts of image)
# - 'thumbnail': Scales images to fit within dimensions while preserving aspect ratio (recommended)
# - 'padded': Scales images to fit within dimensions and adds white padding to maintain exact dimensions

# Thumbnail Sizes
# Maximum dimensions for each thumbnail size (images will be scaled down to fit within these bounds)
THUMBNAIL_SIZES = {
    'small': (400, 400),      # For thumbnails and previews
    'medium': (1000, 1000),   # For medium displays
    'large': (1600, 1600),    # For large displays
    'original': None           # Keep original size
}

# Advanced Settings (usually don't need to change these)
SKIP_OPTIMIZATION_FOR_SMALL_IMAGES = True  # Skip optimization for images smaller than 200KB
SKIP_OPTIMIZATION_FOR_ALREADY_OPTIMAL = True  # Skip optimization for already optimized images
THUMBNAIL_QUALITY_BOOST = 5  # Additional quality boost for thumbnails (0-10)

# File Size Thresholds (in bytes)
SMALL_IMAGE_THRESHOLD = 200 * 1024      # 200KB
OPTIMAL_IMAGE_THRESHOLD = 500 * 1024    # 500KB
WEBP_OPTIMAL_THRESHOLD = 1000 * 1024   # 1MB

# Resampling Methods (automatically selected based on quality preset)
# - Image.Resampling.BICUBIC: Best quality, slower
# - Image.Resampling.LANCZOS: Good quality, balanced
# - Image.Resampling.NEAREST: Fastest, lowest quality

# WebP Compression Methods (automatically selected based on quality preset)
# - 2: Best quality, slowest
# - 4: Better quality, balanced
# - 6: Default quality, faster
# - 0: Fastest, lower quality
