#!/usr/bin/env python
"""
Quality Preset Demonstration Script
This script shows the differences between different quality presets
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

def demonstrate_quality_presets():
    """Demonstrate the differences between quality presets"""
    print("🎨 Quality Preset Demonstration")
    print("=" * 50)
    
    # Show all available presets
    print("📊 Available Quality Presets:")
    print("-" * 30)
    
    for preset_name, settings in ImageOptimizer._QUALITY_PRESETS.items():
        print(f"\n🎯 {preset_name.upper()} Quality:")
        print(f"   - WebP Quality: {settings['webp_quality']}/100")
        print(f"   - JPEG Quality: {settings['jpeg_quality']}/100")
        print(f"   - WebP Method: {settings['webp_method']}")
        print(f"   - Resampling: {settings['resampling']}")
        if 'lossless' in settings:
            print(f"   - Lossless: {settings['lossless']}")
        
        # Explain what each preset is good for
        if preset_name == 'lossless':
            print("   - Best for: Portfolios requiring 100% quality preservation, no quality loss")
            print("   - Trade-off: Largest file sizes, but pixel-perfect quality")
        elif preset_name == 'ultra':
            print("   - Best for: Portfolios, high-end showcases, maximum visual impact")
            print("   - Trade-off: Larger file sizes, slower processing")
        elif preset_name == 'high':
            print("   - Best for: General web use, good balance of quality and size")
            print("   - Trade-off: Moderate file sizes, balanced processing")
        elif preset_name == 'balanced':
            print("   - Best for: Standard web optimization, performance focus")
            print("   - Trade-off: Smaller file sizes, faster processing")
        elif preset_name == 'compressed':
            print("   - Best for: Maximum compression, storage optimization")
            print("   - Trade-off: Smallest file sizes, fastest processing")
    
    print("\n🔧 How to Change Quality Preset:")
    print("-" * 30)
    print("1. Edit: backend/portfolio/optimization_config.py")
    print("2. Change: QUALITY_PRESET = 'ultra'  # or 'high', 'balanced', 'compressed'")
    print("3. Re-optimize images: python manual_optimize.py")
    
    print("\n💡 Recommendations:")
    print("-" * 20)
    print("• Use 'lossless' for 100% quality preservation (no quality loss)")
    print("• Start with 'ultra' for maximum quality")
    print("• Use 'high' for production balance")
    print("• Use 'balanced' if file sizes become too large")
    print("• Use 'compressed' only for maximum storage savings")
    
    print("\n📈 Expected Results:")
    print("-" * 20)
    print("• Lossless: 100% quality, largest files, pixel-perfect preservation")
    print("• Ultra: ~2-3x larger files, ~2-3x slower processing")
    print("• High: ~1.5x larger files, ~1.5x slower processing")
    print("• Balanced: ~1.2x larger files, ~1.2x slower processing")
    print("• Compressed: Smallest files, fastest processing")

def show_current_settings():
    """Show the current optimization settings"""
    print("\n⚙️  Current Settings:")
    print("-" * 20)
    print(f"Quality Preset: {ImageOptimizer.QUALITY_PRESET}")
    print(f"WebP Quality: {ImageOptimizer.get_webp_quality()}/100")
    print(f"WebP Method: {ImageOptimizer.get_webp_method()}")
    print(f"Resampling: {ImageOptimizer.get_resampling_method()}")
    print(f"Thumbnail Method: {ImageOptimizer.THUMBNAIL_METHOD}")
    print(f"Thumbnail Sizes: {ImageOptimizer.THUMBNAIL_SIZES}")

if __name__ == "__main__":
    demonstrate_quality_presets()
    show_current_settings()
    print("\n✅ Demonstration completed!")
    print("\n🚀 Next steps:")
    print("1. Choose your quality preset")
    print("2. Edit optimization_config.py")
    print("3. Test with: python test_new_optimization.py")
    print("4. Optimize images with: python manual_optimize.py")
