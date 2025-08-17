import { useState, useEffect, useRef } from 'react';
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
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    const currentRef = imgRef.current;
    
    if (!currentRef) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observerRef.current?.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '50px'
      }
    );

    observerRef.current.observe(currentRef);

    return () => {
      if (observerRef.current && currentRef) {
        observerRef.current.unobserve(currentRef);
      }
    };
  }, []);

  // Reset state when src changes
  useEffect(() => {
    setImageLoaded(false);
    setImageError(false);
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
    }
  };

  // Show placeholder while not in view or loading
  const showPlaceholder = !isInView || (!imageLoaded && !imageError);

  return (
    <div 
      ref={imgRef}
      className={cn("relative overflow-hidden", className)}
      style={{
        width: width || '100%',
        height: height || '100%',
      }}
      onClick={onClick}
    >
      {/* Placeholder */}
      {showPlaceholder && (
        <div className={cn(
          "absolute inset-0 bg-gray-200 dark:bg-gray-800 flex items-center justify-center transition-opacity duration-300",
          imageLoaded ? "opacity-0" : "opacity-100"
        )}>
          <div className="text-gray-500 dark:text-gray-400 text-sm">
            {!isInView ? 'Loading...' : 'Loading image...'}
          </div>
        </div>
      )}

      {/* Actual Image */}
      {isInView && (
        <img
          src={src}
          alt={alt}
          className={cn(
            "w-full h-full object-cover transition-opacity duration-300",
            imageLoaded ? "opacity-100" : "opacity-0"
          )}
          onLoad={handleLoad}
          onError={handleError}
          loading="lazy"
          decoding="async"
          style={{
            display: imageError ? 'none' : 'block'
          }}
        />
      )}

      {/* Error State */}
      {imageError && (
        <div className={cn(
          "absolute inset-0 bg-gray-100 dark:bg-gray-900 flex items-center justify-center",
          className
        )}>
          <div className="text-center text-gray-500 dark:text-gray-400">
            <div className="text-sm">Image not available</div>
            <div className="text-xs opacity-60 mt-1">Failed to load</div>
          </div>
        </div>
      )}
    </div>
  );
}
