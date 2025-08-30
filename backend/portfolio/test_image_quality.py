#!/usr/bin/env python3
"""
Test script for image quality optimization
Verifies that the new lossless settings are working correctly
"""

import os
import sys
from django.conf import settings
from django.core.management import setup_environ

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from portfolio.image_optimizer import ImageOptimizer

def test_image_quality_settings():
    """Test the current image quality settings"""
    print("=== Image Quality Configuration Test ===\n")
    
    print(f"Production Mode: {ImageOptimizer.PRODUCTION_MODE}")
    print(f"WebP Quality: {ImageOptimizer.WEBP_QUALITY}")
    print(f"JPEG Quality: {ImageOptimizer.JPEG_QUALITY}")
    print(f"WebP Lossless: {ImageOptimizer.WEBP_LOSSLESS}")
    print(f"WebP Method: {ImageOptimizer.WEBP_METHOD}")
    print(f"Thumbnail Method: {ImageOptimizer.THUMBNAIL_METHOD}")
    
    print("\n=== Thumbnail Sizes ===")
    for size_name, dimensions in ImageOptimizer.THUMBNAIL_SIZES.items():
        print(f"{size_name}: {dimensions}")
    
    print("\n=== Quality Assessment ===")
    if ImageOptimizer.PRODUCTION_MODE:
        if ImageOptimizer.WEBP_LOSSLESS:
            print("✅ PRODUCTION MODE: Lossless WebP enabled - 0% quality loss")
        else:
            print("⚠️  PRODUCTION MODE: High quality WebP - minimal quality loss")
    else:
        print("🔧 DEVELOPMENT MODE: High quality WebP - faster processing")
    
    if ImageOptimizer.WEBP_QUALITY == 100:
        print("✅ WebP Quality: Maximum (100) - no quality loss")
    elif ImageOptimizer.WEBP_QUALITY >= 90:
        print("✅ WebP Quality: Very High (90+) - minimal quality loss")
    elif ImageOptimizer.WEBP_QUALITY >= 80:
        print("⚠️  WebP Quality: High (80+) - some quality loss")
    else:
        print("❌ WebP Quality: Low - significant quality loss")
    
    print(f"\n=== Configuration File ===")
    config_path = os.path.join(os.path.dirname(__file__), 'image_optimizer_config.py')
    if os.path.exists(config_path):
        print(f"✅ Configuration file found: {config_path}")
        print("   You can edit this file to switch between production and development modes")
    else:
        print(f"❌ Configuration file not found: {config_path}")
        print("   Using fallback configuration")

if __name__ == "__main__":
    test_image_quality_settings()
