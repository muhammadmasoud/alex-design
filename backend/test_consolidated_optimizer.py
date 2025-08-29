#!/usr/bin/env python
"""
Test script for the new consolidated image optimizer
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.consolidated_image_optimizer import ConsolidatedImageOptimizer, optimize_uploaded_image, get_responsive_image_urls

def test_consolidated_optimizer():
    """Test the new consolidated image optimizer"""
    print("🧪 Testing Consolidated Image Optimizer...")
    
    try:
        # Test optimizer initialization
        optimizer = ConsolidatedImageOptimizer()
        print("✅ ConsolidatedImageOptimizer initialized successfully")
        
        # Test settings
        print(f"   WebP Quality: {optimizer.webp_quality}")
        print(f"   JPEG Quality: {optimizer.jpeg_quality}")
        print(f"   PNG Quality: {optimizer.png_quality}")
        print(f"   Max Dimensions: {optimizer.max_width}x{optimizer.max_height}")
        print(f"   Delete Original: {optimizer.delete_original}")
        print(f"   Thumbnail Sizes: {len(optimizer.thumbnail_sizes)} sizes")
        
        # Test format selection
        test_formats = optimizer._choose_best_format('.png', 'high')
        print(f"   PNG + High Quality → {test_formats}")
        
        test_formats = optimizer._choose_best_format('.jpg', 'medium')
        print(f"   JPG + Medium Quality → {test_formats}")
        
        test_formats = optimizer._choose_best_format('.gif', 'low')
        print(f"   GIF + Low Quality → {test_formats}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error testing optimizer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consolidated_optimizer()
