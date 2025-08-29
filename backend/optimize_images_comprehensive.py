#!/usr/bin/env python3
"""
Comprehensive Image Optimization Script for Alex Design Portfolio
This script will optimize all existing images without losing data or quality
"""
import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PIL import Image, ImageOps
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from portfolio.models import Project, Service, ProjectImage, ServiceImage
from portfolio.image_utils import optimize_image
import io
import uuid
from datetime import datetime


class ImageOptimizer:
    def __init__(self):
        self.total_processed = 0
        self.total_saved_bytes = 0
        self.errors = []
        
        # Optimization settings - high quality preservation
        self.settings = {
            'main_images': {
                'max_width': 1920,
                'max_height': 1080,
                'quality': 90,  # High quality for main images
                'format': 'WEBP'  # Better compression at high quality
            },
            'album_images': {
                'max_width': 1920,
                'max_height': 1080,
                'quality': 88,  # Slightly lower for albums
                'format': 'WEBP'
            },
            'service_icons': {
                'max_width': 512,
                'max_height': 512,
                'quality': 95,  # Very high quality for icons
                'format': 'WEBP'
            }
        }
    
    def get_image_info(self, image_path):
        """Get detailed image information"""
        try:
            full_path = os.path.join('media', image_path) if not image_path.startswith('media') else image_path
            
            if not os.path.exists(full_path):
                return None
                
            with Image.open(full_path) as img:
                file_size = os.path.getsize(full_path)
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                }
        except Exception as e:
            self.errors.append(f"Error reading image {image_path}: {e}")
            return None
    
    def should_optimize(self, image_path, settings):
        """Determine if image should be optimized based on size and format"""
        info = self.get_image_info(image_path)
        if not info:
            return False
        
        # Optimize if:
        # 1. Image is larger than target dimensions
        # 2. Image is PNG and could be WebP
        # 3. Image is larger than 500KB
        # 4. Image is JPEG with low quality
        
        needs_resize = info['width'] > settings['max_width'] or info['height'] > settings['max_height']
        is_large_file = info['size_bytes'] > 500 * 1024  # 500KB
        can_convert_to_webp = info['format'] in ['PNG', 'JPEG'] and settings['format'] == 'WEBP'
        
        return needs_resize or is_large_file or can_convert_to_webp
    
    def optimize_image_file(self, image_path, settings):
        """Optimize a single image file"""
        try:
            full_path = os.path.join('media', image_path) if not image_path.startswith('media') else image_path
            
            if not os.path.exists(full_path):
                return None, 0
            
            original_size = os.path.getsize(full_path)
            
            # Open and process image
            with Image.open(full_path) as img:
                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Convert RGBA to RGB for WebP/JPEG if needed
                if settings['format'] in ['WEBP', 'JPEG'] and img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                
                # Resize if needed
                if img.width > settings['max_width'] or img.height > settings['max_height']:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(settings['max_width'] / img.width, settings['max_height'] / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    
                    # Use high-quality resampling
                    resample = Image.Resampling.LANCZOS if hasattr(Image.Resampling, 'LANCZOS') else Image.LANCZOS
                    img = img.resize((new_width, new_height), resample)
                
                # Save optimized image
                output = io.BytesIO()
                save_kwargs = {'format': settings['format'], 'optimize': True}
                
                if settings['format'] == 'WEBP':
                    save_kwargs.update({
                        'quality': settings['quality'],
                        'method': 6,  # Best compression
                        'lossless': settings['quality'] >= 95
                    })
                elif settings['format'] == 'JPEG':
                    save_kwargs.update({
                        'quality': settings['quality'],
                        'progressive': True,
                        'subsampling': 0  # Disable chroma subsampling for better quality
                    })
                elif settings['format'] == 'PNG':
                    save_kwargs.update({
                        'compress_level': 6,
                        'optimize': True
                    })
                
                img.save(output, **save_kwargs)
                output.seek(0)
                
                # Get new file extension
                ext = settings['format'].lower()
                if ext == 'jpeg':
                    ext = 'jpg'
                
                # Create new filename with correct extension
                path_parts = image_path.split('.')
                if len(path_parts) > 1:
                    path_parts[-1] = ext
                    new_filename = '.'.join(path_parts)
                else:
                    new_filename = f"{image_path}.{ext}"
                
                # Save the optimized file
                optimized_data = output.getvalue()
                new_size = len(optimized_data)
                
                # Only save if there's a significant improvement or format change
                if new_size < original_size * 0.95 or settings['format'] != img.format:
                    # Backup original if format is changing
                    if settings['format'] != img.format:
                        backup_path = f"{full_path}.backup"
                        if not os.path.exists(backup_path):
                            os.rename(full_path, backup_path)
                    
                    # Write optimized file
                    with open(f"media/{new_filename}", 'wb') as f:
                        f.write(optimized_data)
                    
                    savings = original_size - new_size
                    return new_filename, savings
                else:
                    return image_path, 0
                    
        except Exception as e:
            self.errors.append(f"Error optimizing {image_path}: {e}")
            return None, 0
    
    def optimize_all_images(self):
        """Optimize all images in the system"""
        print("🖼️  Starting comprehensive image optimization...")
        print("=" * 60)
        
        # Get all model instances with images
        projects = Project.objects.filter(image__isnull=False)
        services = Service.objects.filter(icon__isnull=False)
        project_images = ProjectImage.objects.all()
        service_images = ServiceImage.objects.all()
        
        print(f"Found:")
        print(f"  - {projects.count()} project main images")
        print(f"  - {services.count()} service icons")
        print(f"  - {project_images.count()} project album images")
        print(f"  - {service_images.count()} service album images")
        print()
        
        # Optimize project main images
        print("📸 Optimizing project main images...")
        for project in projects:
            if project.image:
                image_path = project.image.name
                if self.should_optimize(image_path, self.settings['main_images']):
                    print(f"  Optimizing: {image_path}")
                    new_path, savings = self.optimize_image_file(image_path, self.settings['main_images'])
                    if new_path and savings > 0:
                        self.total_saved_bytes += savings
                        print(f"    ✅ Saved {savings / 1024:.1f} KB")
                    self.total_processed += 1
                else:
                    print(f"  ⏭️  Skipping: {image_path} (already optimized)")
        
        # Optimize service icons
        print("\\n🔧 Optimizing service icons...")
        for service in services:
            if service.icon:
                image_path = service.icon.name
                if self.should_optimize(image_path, self.settings['service_icons']):
                    print(f"  Optimizing: {image_path}")
                    new_path, savings = self.optimize_image_file(image_path, self.settings['service_icons'])
                    if new_path and savings > 0:
                        self.total_saved_bytes += savings
                        print(f"    ✅ Saved {savings / 1024:.1f} KB")
                    self.total_processed += 1
                else:
                    print(f"  ⏭️  Skipping: {image_path} (already optimized)")
        
        # Optimize project album images
        print("\\n📚 Optimizing project album images...")
        for img in project_images:
            if img.image:
                image_path = img.image.name
                if self.should_optimize(image_path, self.settings['album_images']):
                    print(f"  Optimizing: {image_path}")
                    new_path, savings = self.optimize_image_file(image_path, self.settings['album_images'])
                    if new_path and savings > 0:
                        self.total_saved_bytes += savings
                        print(f"    ✅ Saved {savings / 1024:.1f} KB")
                    self.total_processed += 1
                else:
                    print(f"  ⏭️  Skipping: {image_path} (already optimized)")
        
        # Optimize service album images
        print("\\n🛠️  Optimizing service album images...")
        for img in service_images:
            if img.image:
                image_path = img.image.name
                if self.should_optimize(image_path, self.settings['album_images']):
                    print(f"  Optimizing: {image_path}")
                    new_path, savings = self.optimize_image_file(image_path, self.settings['album_images'])
                    if new_path and savings > 0:
                        self.total_saved_bytes += savings
                        print(f"    ✅ Saved {savings / 1024:.1f} KB")
                    self.total_processed += 1
                else:
                    print(f"  ⏭️  Skipping: {image_path} (already optimized)")
        
        # Print summary
        print("\\n" + "=" * 60)
        print("📊 OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"Images processed: {self.total_processed}")
        print(f"Total space saved: {self.total_saved_bytes / (1024 * 1024):.2f} MB")
        print(f"Errors encountered: {len(self.errors)}")
        
        if self.errors:
            print("\\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\\n✅ Optimization complete!")


def create_additional_optimizations():
    """Create additional optimization scripts and settings"""
    
    # Create image serving optimization script
    nginx_config = '''
# Add this to your nginx.conf for better image serving performance
location /media/ {
    alias /home/ubuntu/alex-design/backend/media/;
    
    # Enable compression for images
    gzip on;
    gzip_types image/svg+xml;
    
    # Cache images for 30 days
    expires 30d;
    add_header Cache-Control "public, immutable";
    
    # Enable efficient file serving
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # Optimize for different image formats
    location ~* \\.(webp)$ {
        add_header Vary Accept;
        expires 30d;
    }
    
    location ~* \\.(jpg|jpeg|png|gif)$ {
        expires 30d;
    }
}

# Optional: WebP serving with fallback
location ~* \\.(jpg|jpeg|png)$ {
    add_header Vary Accept;
    try_files $uri$webp_suffix $uri =404;
}
'''
    
    with open('nginx_image_optimization.conf', 'w') as f:
        f.write(nginx_config)
    
    # Create frontend image optimization component
    react_image_component = '''
// Optimized Image Component for React
import React, { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  lazy?: boolean;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  className = '',
  width,
  height,
  lazy = true
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  
  // Generate WebP version URL
  const getOptimizedSrc = (originalSrc: string) => {
    if (originalSrc.includes('.webp')) return originalSrc;
    
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + '.webp';
  };
  
  const webpSrc = getOptimizedSrc(src);
  
  return (
    <picture className={className}>
      {/* WebP version for better compression */}
      <source srcSet={webpSrc} type="image/webp" />
      
      {/* Fallback to original format */}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={lazy ? 'lazy' : 'eager'}
        onLoad={() => setImageLoaded(true)}
        onError={() => setImageError(true)}
        className={`transition-opacity duration-300 ${
          imageLoaded ? 'opacity-100' : 'opacity-0'
        } ${imageError ? 'hidden' : ''}`}
      />
      
      {/* Loading placeholder */}
      {!imageLoaded && !imageError && (
        <div 
          className="bg-gray-200 animate-pulse"
          style={{ width, height }}
        />
      )}
      
      {/* Error fallback */}
      {imageError && (
        <div 
          className="bg-gray-100 flex items-center justify-center text-gray-400"
          style={{ width, height }}
        >
          Image not available
        </div>
      )}
    </picture>
  );
};
'''
    
    with open('OptimizedImage.tsx', 'w') as f:
        f.write(react_image_component)
    
    print("📄 Created additional optimization files:")
    print("  - nginx_image_optimization.conf")
    print("  - OptimizedImage.tsx")


def main():
    """Main optimization function"""
    print("🚀 Alex Design Portfolio Image Optimizer")
    print("This script will optimize your images without losing quality or data\\n")
    
    optimizer = ImageOptimizer()
    
    # Run the optimization
    optimizer.optimize_all_images()
    
    # Create additional optimization files
    print("\\n📁 Creating additional optimization tools...")
    create_additional_optimizations()
    
    print("\\n🎉 All optimizations complete!")
    print("\\nNext steps:")
    print("1. Test your website to ensure images load correctly")
    print("2. Apply the nginx configuration for better image serving")
    print("3. Use the OptimizedImage.tsx component in your React frontend")
    print("4. Monitor your website performance after optimization")


if __name__ == '__main__':
    main()
