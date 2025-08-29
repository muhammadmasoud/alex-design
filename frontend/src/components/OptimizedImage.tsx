import React, { useState, useRef } from 'react';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  effect?: 'blur' | 'black-and-white' | 'opacity';
  placeholder?: string;
  onError?: (e: any) => void;
  onClick?: () => void;
  enableWebP?: boolean;
  quality?: 'low' | 'medium' | 'high';
}

export default function OptimizedImage({
  src,
  alt,
  className,
  width,
  height,
  effect = 'blur',
  placeholder = '/placeholder.svg',
  onError,
  onClick,
  enableWebP = true,
  quality = 'high',
}: OptimizedImageProps) {
  const [imageError, setImageError] = useState(false);
  const [fallbackUsed, setFallbackUsed] = useState(false);

  // Generate WebP version URL
  const getWebPSrc = (originalSrc: string) => {
    if (!enableWebP || originalSrc.includes('.webp')) return originalSrc;
    
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + '.webp';
  };

  // Generate quality-based URL (if your backend supports it)
  const getQualitySrc = (originalSrc: string) => {
    if (quality === 'high') return originalSrc;
    
    const qualityParams = {
      low: '_q50',
      medium: '_q75',
      high: ''
    };
    
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + qualityParams[quality] + originalSrc.substring(lastDot);
  };

  const handleError = (e: any) => {
    if (!fallbackUsed && enableWebP) {
      // Try fallback to original format
      setFallbackUsed(true);
      const target = e.target as HTMLImageElement;
      target.src = src;
      return;
    }

    setImageError(true);
    if (onError) {
      onError(e);
    } else {
      // Default error handling
      const target = e.target as HTMLImageElement;
      target.src = placeholder;
    }
  };

  // Determine the best source to use
  const optimizedSrc = fallbackUsed ? src : getQualitySrc(getWebPSrc(src));

  // If we're using WebP, create a picture element for better fallback support
  if (enableWebP && !fallbackUsed && !imageError) {
    return (
      <picture className={cn("block", className)}>
        <source srcSet={getWebPSrc(src)} type="image/webp" />
        <source srcSet={src} type={src.includes('.png') ? 'image/png' : 'image/jpeg'} />
        <LazyLoadImage
          src={src}
          alt={alt}
          width={width}
          height={height}
          effect={effect}
          className="w-full h-full object-cover"
          onError={handleError}
          onClick={onClick}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block'
          }}
          placeholder={
            <div className={cn(
              "bg-muted animate-pulse flex items-center justify-center",
              className
            )}>
              <div className="text-muted-foreground text-sm">Loading...</div>
            </div>
          }
          loading="lazy"
          decoding="async"
        />
      </picture>
    );
  }

  return (
    <LazyLoadImage
      src={optimizedSrc}
      alt={alt}
      width={width}
      height={height}
      effect={effect}
      className={cn(className)}
      onError={handleError}
      onClick={onClick}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        display: 'block'
      }}
      placeholder={
        <div className={cn(
          "bg-muted animate-pulse flex items-center justify-center",
          className
        )}>
          <div className="text-muted-foreground text-sm">Loading...</div>
        </div>
      }
      loading="lazy"
      decoding="async"
    />
  );
}

// Additional optimized gallery component
interface OptimizedImageGalleryProps {
  images: Array<{
    src: string;
    alt: string;
    title?: string;
  }>;
  columns?: 1 | 2 | 3 | 4;
  className?: string;
  quality?: 'low' | 'medium' | 'high';
}

export function OptimizedImageGallery({
  images,
  columns = 3,
  className = '',
  quality = 'medium', // Use medium quality for galleries
}: OptimizedImageGalleryProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className={cn(`grid gap-4 ${gridCols[columns]}`, className)}>
      {images.map((image, index) => (
        <div key={index} className="group relative aspect-square overflow-hidden rounded-lg bg-muted">
          <OptimizedImage
            src={image.src}
            alt={image.alt}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            quality={quality}
            enableWebP={true}
            placeholder="/placeholder.svg"
          />
          {image.title && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-2">
              <div className="text-sm font-medium truncate">{image.title}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
