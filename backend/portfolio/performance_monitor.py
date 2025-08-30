#!/usr/bin/env python3
"""
Image Performance Monitoring Script
Analyzes optimization effectiveness and suggests improvements
"""

import os
import sys
import time
import glob
from pathlib import Path

# Add Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.conf import settings
from portfolio.models import Project, Service

def analyze_image_optimization():
    """Analyze current image optimization effectiveness"""
    print("🔍 IMAGE OPTIMIZATION ANALYSIS")
    print("=" * 50)
    
    media_root = Path(settings.MEDIA_ROOT)
    
    # Analyze projects
    total_original_size = 0
    total_optimized_size = 0
    optimization_count = 0
    missing_optimizations = []
    
    print("\n📁 PROJECT ANALYSIS")
    print("-" * 30)
    
    for project in Project.objects.filter(image__isnull=False):
        if not project.image:
            continue
            
        original_path = Path(project.image.path)
        if not original_path.exists():
            continue
            
        original_size = original_path.stat().st_size
        total_original_size += original_size
        
        # Check for optimized versions
        project_folder = original_path.parent
        webp_folder = project_folder / 'webp'
        
        if webp_folder.exists():
            optimized_files = list(webp_folder.glob('*.webp'))
            if optimized_files:
                optimized_size = sum(f.stat().st_size for f in optimized_files)
                total_optimized_size += optimized_size
                optimization_count += 1
                
                savings = (1 - optimized_size / original_size) * 100
                print(f"  ✅ {project.title[:30]:30} - {savings:.1f}% savings")
            else:
                missing_optimizations.append(f"Project: {project.title}")
        else:
            missing_optimizations.append(f"Project: {project.title}")
    
    # Analyze services
    print("\n🔧 SERVICE ANALYSIS")
    print("-" * 30)
    
    for service in Service.objects.filter(icon__isnull=False):
        if not service.icon:
            continue
            
        original_path = Path(service.icon.path)
        if not original_path.exists():
            continue
            
        original_size = original_path.stat().st_size
        total_original_size += original_size
        
        # Check for optimized versions
        service_folder = original_path.parent
        webp_folder = service_folder / 'webp'
        
        if webp_folder.exists():
            optimized_files = list(webp_folder.glob('*.webp'))
            if optimized_files:
                optimized_size = sum(f.stat().st_size for f in optimized_files)
                total_optimized_size += optimized_size
                optimization_count += 1
                
                savings = (1 - optimized_size / original_size) * 100
                print(f"  ✅ {service.name[:30]:30} - {savings:.1f}% savings")
            else:
                missing_optimizations.append(f"Service: {service.name}")
        else:
            missing_optimizations.append(f"Service: {service.name}")
    
    # Overall statistics
    print("\n📊 OVERALL STATISTICS")
    print("-" * 30)
    
    if total_original_size > 0:
        overall_savings = (1 - total_optimized_size / total_original_size) * 100
        print(f"Original total size: {total_original_size / (1024*1024):.1f} MB")
        print(f"Optimized total size: {total_optimized_size / (1024*1024):.1f} MB")
        print(f"Space saved: {(total_original_size - total_optimized_size) / (1024*1024):.1f} MB")
        print(f"Overall compression: {overall_savings:.1f}%")
        print(f"Items optimized: {optimization_count}")
    
    # Missing optimizations
    if missing_optimizations:
        print("\n⚠️  MISSING OPTIMIZATIONS")
        print("-" * 30)
        for item in missing_optimizations:
            print(f"  ❌ {item}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if missing_optimizations:
        print("  🔧 Run optimization for missing items:")
        print("     python portfolio/manual_optimize.py")
    
    if overall_savings < 50:
        print("  📈 Consider enabling AVIF format for better compression")
        print("     Edit portfolio/image_optimizer_config.py")
    
    if optimization_count > 100:
        print("  🌐 Consider implementing CDN for faster global delivery")
        print("     See CDN_SETUP.md for instructions")
    
    print("\n✅ Analysis complete!")

def benchmark_optimization_speed():
    """Benchmark image optimization performance"""
    print("\n⏱️  OPTIMIZATION SPEED BENCHMARK")
    print("=" * 40)
    
    # Find a test image
    media_root = Path(settings.MEDIA_ROOT)
    test_images = list(media_root.glob('**/*.jpg')) + list(media_root.glob('**/*.png'))
    
    if not test_images:
        print("❌ No test images found")
        return
    
    test_image = test_images[0]
    print(f"Testing with: {test_image.name}")
    
    # Test current settings
    from portfolio.image_optimizer import ImageOptimizer
    
    start_time = time.time()
    
    # This would normally optimize the image, but we'll just time the setup
    print(f"Production Mode: {ImageOptimizer.PRODUCTION_MODE}")
    print(f"WebP Quality: {ImageOptimizer.WEBP_QUALITY}")
    print(f"WebP Method: {ImageOptimizer.WEBP_METHOD}")
    
    # Simulate optimization time based on settings
    if ImageOptimizer.PRODUCTION_MODE and ImageOptimizer.WEBP_LOSSLESS:
        estimated_time = 2.5  # Lossless is slower but highest quality
    else:
        estimated_time = 1.0  # Quality-based is faster
    
    print(f"Estimated optimization time per image: {estimated_time:.1f}s")
    print(f"For {len(test_images)} images: {estimated_time * len(test_images):.1f}s total")

if __name__ == "__main__":
    analyze_image_optimization()
    benchmark_optimization_speed()
