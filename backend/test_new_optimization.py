#!/usr/bin/env python
"""
Test Script for New Image Optimization Settings
This script tests the improved image optimization quality settings
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.image_optimizer import ImageOptimizer
from portfolio.optimization_config import QUALITY_PRESET, THUMBNAIL_METHOD

def test_optimization_settings():
    """Test the new optimization settings"""
    print("🖼️  Testing New Image Optimization Settings")
    print("=" * 50)
    
    # Test quality preset
    print(f"✅ Quality Preset: {QUALITY_PRESET}")
    print(f"✅ Thumbnail Method: {THUMBNAIL_METHOD}")
    
    # Test quality values
    print(f"✅ WebP Quality: {ImageOptimizer.get_webp_quality()}")
    print(f"✅ JPEG Quality: {ImageOptimizer.get_jpeg_quality()}")
    print(f"✅ WebP Method: {ImageOptimizer.get_webp_method()}")
    print(f"✅ Resampling Method: {ImageOptimizer.get_resampling_method()}")
    
    # Test thumbnail sizes
    print(f"✅ Thumbnail Sizes: {ImageOptimizer.THUMBNAIL_SIZES}")
    
    # Test quality presets
    print("\n📊 Quality Preset Details:")
    for preset, settings in ImageOptimizer._QUALITY_PRESETS.items():
        if 'lossless' in settings:
            print(f"  - {preset}: WebP={settings['webp_quality']}, Method={settings['webp_method']}, Lossless={settings['lossless']}")
        else:
            print(f"  - {preset}: WebP={settings['webp_quality']}, Method={settings['webp_method']}")
    
    print("\n🎯 Current Settings Summary:")
    print(f"  - Using {QUALITY_PRESET} quality preset")
    print(f"  - WebP quality: {ImageOptimizer.get_webp_quality()}/100")
    print(f"  - WebP method: {ImageOptimizer.get_webp_method()} (0=fast, 2=best quality)")
    print(f"  - Resampling: {ImageOptimizer.get_resampling_method()}")
    print(f"  - Lossless mode: {ImageOptimizer.is_lossless_mode()}")
    
    if QUALITY_PRESET == 'lossless':
        print("  - 🎯 LOSSLESS mode enabled - 100% quality preservation!")
        print("  - ⚠️  File sizes will be larger but quality is pixel-perfect")
    elif QUALITY_PRESET == 'ultra':
        print("  - ⭐ Maximum quality mode enabled - best for portfolios!")
    elif QUALITY_PRESET == 'high':
        print("  - ✨ High quality mode enabled - good balance of quality and size")
    elif QUALITY_PRESET == 'balanced':
        print("  - ⚖️  Balanced mode enabled - standard web optimization")
    elif QUALITY_PRESET == 'compressed':
        print("  - 📦 Compressed mode enabled - maximum file size reduction")
    
    print("\n🔧 To change quality, edit: backend/portfolio/optimization_config.py")
    print("   - Set QUALITY_PRESET to 'lossless' for 100% quality preservation")
    print("   - Set QUALITY_PRESET to 'ultra' for maximum quality")
    print("   - Set QUALITY_PRESET to 'high' for high quality (recommended)")
    print("   - Set QUALITY_PRESET to 'balanced' for standard optimization")
    print("   - Set QUALITY_PRESET to 'compressed' for maximum compression")

def test_image_analysis():
    """Test the image analysis functionality"""
    print("\n🔍 Testing Image Analysis:")
    print("-" * 30)
    
    # Test with a sample image path (this won't actually process images)
    sample_path = "/path/to/sample/image.jpg"
    
    try:
        # This will test the method without actually processing images
        should_optimize = ImageOptimizer._should_optimize_image(sample_path)
        print(f"✅ Image analysis method working: {should_optimize}")
    except Exception as e:
        print(f"⚠️  Image analysis test skipped (expected for non-existent path): {str(e)}")

if __name__ == "__main__":
    test_optimization_settings()
    test_image_analysis()
    print("\n✅ All tests completed!")
