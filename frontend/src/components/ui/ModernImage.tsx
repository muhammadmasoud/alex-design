/**
 * Modern Image Component with Progressive Enhancement
 * Supports WebP, AVIF with fallbacks and lazy loading
 */

import React, { useState, useEffect, useRef } from 'react';

interface ModernImageProps {
  src: string;
  alt: string;
  className?: string;
  sizes?: {
    small?: string;
    medium?: string;
    large?: string;
  };
  loading?: 'lazy' | 'eager';
  quality?: 'small' | 'medium' | 'large';
  onLoad?: () => void;
  onError?: () => void;
}

export const ModernImage: React.FC<ModernImageProps> = ({
  src,
  alt,
  className = '',
  sizes,
  loading = 'lazy',
  quality = 'medium',
  onLoad,
  onError
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Generate optimized image URLs
  const getOptimizedUrl = (format: 'avif' | 'webp' | 'jpg', size: string = quality) => {
    if (!src) return '';
    
    // Extract path parts
    const parts = src.split('/');
    const filename = parts[parts.length - 1];
    const name = filename.split('.')[0];
    const path = parts.slice(0, -1).join('/');
    
    // Generate optimized path
    if (src.includes('/media/projects/') || src.includes('/media/services/')) {
      switch (format) {
        case 'avif':
          return `${path}/webp/${name}.avif`;
        case 'webp':
          return `${path}/webp/${name}_${size}.webp`;
        case 'jpg':
          return `${path}/webp/${name}_progressive.jpg`;
        default:
          return src;
      }
    }
    
    return src;
  };

  // Handle image load
  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  // Handle image error
  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (loading === 'lazy' && imgRef.current) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement;
              img.src = img.dataset.src || '';
              observer.unobserve(img);
            }
          });
        },
        { threshold: 0.1 }
      );

      observer.observe(imgRef.current);
      return () => observer.disconnect();
    }
  }, [loading]);

  // Generate sizes attribute for responsive images
  const sizesAttr = sizes ? Object.values(sizes).join(', ') : undefined;

  return (
    <div className={`modern-image-container ${className}`}>
      <picture>
        {/* AVIF format (best compression) */}
        <source
          srcSet={`
            ${getOptimizedUrl('avif', 'small')} 400w,
            ${getOptimizedUrl('avif', 'medium')} 1000w,
            ${getOptimizedUrl('avif', 'large')} 1600w
          `}
          sizes={sizesAttr}
          type="image/avif"
        />
        
        {/* WebP format (good compression, wide support) */}
        <source
          srcSet={`
            ${getOptimizedUrl('webp', 'small')} 400w,
            ${getOptimizedUrl('webp', 'medium')} 1000w,
            ${getOptimizedUrl('webp', 'large')} 1600w
          `}
          sizes={sizesAttr}
          type="image/webp"
        />
        
        {/* JPEG fallback (universal support) */}
        <source
          srcSet={`
            ${getOptimizedUrl('jpg', 'small')} 400w,
            ${getOptimizedUrl('jpg', 'medium')} 1000w,
            ${getOptimizedUrl('jpg', 'large')} 1600w
          `}
          sizes={sizesAttr}
          type="image/jpeg"
        />
        
        {/* Fallback img tag */}
        <img
          ref={imgRef}
          src={loading === 'lazy' ? undefined : getOptimizedUrl('webp')}
          data-src={loading === 'lazy' ? getOptimizedUrl('webp') : undefined}
          alt={alt}
          className={`
            transition-opacity duration-300
            ${isLoaded ? 'opacity-100' : 'opacity-0'}
            ${hasError ? 'bg-gray-200' : ''}
          `}
          onLoad={handleLoad}
          onError={handleError}
          loading={loading}
          decoding="async"
        />
      </picture>
      
      {/* Loading placeholder */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded-lg" />
      )}
      
      {/* Error placeholder */}
      {hasError && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center rounded-lg">
          <span className="text-gray-400 text-sm">Image not available</span>
        </div>
      )}
    </div>
  );
};

export default ModernImage;
