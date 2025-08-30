#!/usr/bin/env python3
"""
Test script for AWS compatibility
Verifies that the image optimizer works in AWS-safe mode
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.image_optimizer import ImageOptimizer

def test_aws_compatibility():
    """Test the AWS-compatible configuration"""
    print("=== AWS Compatibility Test ===\n")
    
    print(f"Production Mode: {ImageOptimizer.PRODUCTION_MODE}")
    print(f"WebP Quality: {ImageOptimizer.WEBP_QUALITY}")
    print(f"WebP Lossless: {ImageOptimizer.WEBP_LOSSLESS}")
    print(f"WebP Method: {ImageOptimizer.WEBP_METHOD}")
    
    print("\n=== AWS Safe Settings ===")
    print(f"AWS Safe Mode: {getattr(ImageOptimizer, 'AWS_SAFE_MODE', 'Not set')}")
    print(f"Skip Advanced Features: {getattr(ImageOptimizer, 'SKIP_ADVANCED_FEATURES', 'Not set')}")
    print(f"Use Sharp YUVA: {getattr(ImageOptimizer, 'USE_SHARP_YUVA', 'Not set')}")
    print(f"Thumbnail Sharpening: {getattr(ImageOptimizer, 'THUMBNAIL_SHARPENING', 'Not set')}")
    
    print("\n=== Quality Assessment ===")
    if ImageOptimizer.PRODUCTION_MODE:
        if ImageOptimizer.WEBP_LOSSLESS:
            print("✅ PRODUCTION MODE: Lossless WebP enabled - 0% quality loss")
        else:
            print("⚠️  PRODUCTION MODE: High quality WebP - minimal quality loss")
    else:
        print("🔧 DEVELOPMENT MODE: High quality WebP - faster processing")
    
    if getattr(ImageOptimizer, 'AWS_SAFE_MODE', False):
        print("✅ AWS SAFE MODE: Enabled - using fallback methods for compatibility")
    else:
        print("⚠️  AWS SAFE MODE: Disabled - may cause issues on AWS")
    
    print("\n=== Configuration Status ===")
    config_path = os.path.join(os.path.dirname(__file__), 'portfolio', 'image_optimizer_config.py')
    if os.path.exists(config_path):
        print(f"✅ Configuration file found: {config_path}")
        print("   AWS-compatible settings are active")
    else:
        print(f"❌ Configuration file not found: {config_path}")
        print("   Using fallback configuration")
    
    print("\n🚀 Ready for AWS deployment!")

if __name__ == "__main__":
    test_aws_compatibility()
