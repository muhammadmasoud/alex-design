import React, { useState, useRef } from 'react';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { cn } from '@/lib/utils';
import { isApiImage } from '@/lib/imageUtils';

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
  
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Generate WebP version URL only for non-API images
  const getWebPSrc = (originalSrc: string) => {
    if (!enableWebP || originalSrc.includes('.webp') || isApiImage(originalSrc)) return originalSrc;
    
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + '.webp';
  };

  // For API images, use the URL as-is since it's already optimized
  // For non-API images, generate quality-based URL if needed
  const getQualitySrc = (originalSrc: string) => {
    if (isApiImage(originalSrc) || quality === 'high') return originalSrc;
    
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
    if (!fallbackUsed && enableWebP && !isApiImage(src)) {
      // Try fallback to original format only for non-API images
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

  // If we're using WebP and it's not an API image, create a picture element for better fallback support
  if (enableWebP && !fallbackUsed && !imageError && !isApiImage(src)) {
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
  className?: string;
}

export const OptimizedImageGallery: React.FC<OptimizedImageGalleryProps> = ({
  images,
  className = ''
}) => {
  return (
    <div className={cn("grid gap-4", className)}>
      {images.map((image, index) => (
        <OptimizedImage
          key={index}
          src={image.src}
          alt={image.alt}
          className="w-full h-auto"
        />
      ))}
    </div>
  );
};
