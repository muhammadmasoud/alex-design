import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

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
}: OptimizedImageProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [imageSrc, setImageSrc] = useState(src);

  // Reset state when src changes
  useEffect(() => {
    setImageLoaded(false);
    setImageError(false);
    setImageSrc(src);
  }, [src]);

  const handleLoad = () => {
    setImageLoaded(true);
    setImageError(false);
  };

  const handleError = (e: any) => {
    console.warn('Image failed to load:', src);
    setImageError(true);
    setImageLoaded(false);
    
    if (onError) {
      onError(e);
    } else {
      // Try to refresh the image URL by adding a cache-busting parameter
      if (!imageSrc.includes('?refresh=')) {
        const refreshedSrc = `${src}?refresh=${Date.now()}`;
        setImageSrc(refreshedSrc);
        return;
      }
      
      // If refresh attempt also failed, use placeholder
      const target = e.target as HTMLImageElement;
      target.src = placeholder;
    }
  };

  // If image failed to load and we've tried refresh, show placeholder
  if (imageError && imageSrc.includes('?refresh=')) {
    return (
      <div className={cn(
        "bg-muted flex items-center justify-center text-muted-foreground",
        className
      )}>
        <div className="text-center">
          <div className="text-sm">Image not available</div>
          <div className="text-xs opacity-60 mt-1">Click to retry</div>
        </div>
      </div>
    );
  }

  return (
    <LazyLoadImage
      src={imageSrc}
      alt={alt}
      width={width}
      height={height}
      effect={effect}
      className={cn(className)}
      onLoad={handleLoad}
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
      // Additional performance optimizations
      loading="lazy"
      decoding="async"
      // Add better caching behavior
      beforeLoad={() => {
        // Ensure we don't show stale cached images
        const img = new Image();
        img.src = imageSrc;
        return true;
      }}
    />
  );
}
