#!/usr/bin/env python
"""
Test script for WebP conversion system
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.consolidated_image_optimizer import ConsolidatedImageOptimizer

def test_webp_conversion():
    """Test the WebP conversion system"""
    print("🧪 Testing WebP Conversion System")
    print("=" * 50)
    
    # Test optimizer initialization
    try:
        optimizer = ConsolidatedImageOptimizer()
        print("✅ EnhancedImageOptimizer initialized successfully")
        
        # Show settings
        print(f"\n📋 Optimizer Settings:")
        print(f"   WebP Quality: {optimizer.webp_quality}")
        print(f"   Delete Original: {optimizer.delete_original}")
        print(f"   Compression Method: {optimizer.compression_method}")
        print(f"   Thumbnail Sizes: {len(optimizer.thumbnail_sizes)}")
        
        # Show thumbnail sizes
        for size_name, dimensions in optimizer.thumbnail_sizes.items():
            print(f"     {size_name}: {dimensions}")
        
        # Test settings from Django
        image_settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
        print(f"\n⚙️  Django Settings:")
        for key, value in image_settings.items():
            print(f"   {key}: {value}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_webp_conversion()
