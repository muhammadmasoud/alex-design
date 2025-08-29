#!/usr/bin/env python3
"""
Image analysis script to check current optimization status
"""
from PIL import Image
import os

def analyze_images():
    media_path = 'media'
    image_files = []
    
    # Find all image files
    for root, dirs, files in os.walk(media_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                full_path = os.path.join(root, file)
                try:
                    with Image.open(full_path) as img:
                        size_mb = os.path.getsize(full_path) / (1024 * 1024)
                        image_files.append({
                            'file': full_path,
                            'dimensions': f'{img.width}x{img.height}',
                            'format': img.format,
                            'size_mb': round(size_mb, 2),
                            'needs_optimization': size_mb > 0.5 or img.width > 1920 or img.height > 1080
                        })
                except Exception as e:
                    print(f'Error reading {full_path}: {e}')
    
    # Sort by size and show results
    image_files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    print('Image Analysis Report:')
    print('=' * 80)
    print(f'{"File":<60} {"Dimensions":<12} {"Format":<8} {"Size(MB)":<8} {"Optimize?"}')
    print('-' * 80)
    
    for img in image_files:
        optimize = 'YES' if img['needs_optimization'] else 'NO'
        filename = img['file'].replace('media\\', '').replace('media/', '')
        print(f'{filename:<60} {img["dimensions"]:<12} {img["format"]:<8} {img["size_mb"]:<8} {optimize}')
    
    print(f'\nTotal images: {len(image_files)}')
    print(f'Images needing optimization: {sum(1 for img in image_files if img["needs_optimization"])}')
    
    # Calculate potential savings
    total_size = sum(img['size_mb'] for img in image_files)
    print(f'Total current size: {total_size:.2f} MB')
    
    return image_files

if __name__ == '__main__':
    analyze_images()
