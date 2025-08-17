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
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Check if image is already cached/loaded
  const checkImageCache = (imageSrc: string): Promise<boolean> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      // If image loads immediately (cached), onload fires synchronously
      img.src = imageSrc;
      
      // Check if image is already complete (cached)
      if (img.complete) {
        resolve(true);
      }
    });
  };

  // Initialize image loading state
  useEffect(() => {
    let mounted = true;

    const initializeImage = async () => {
      setImageLoaded(false);
      setImageError(false);

      // Check if image is cached first
      const isCached = await checkImageCache(src);
      
      if (mounted && isCached) {
        // Image is cached, show it immediately
        setImageLoaded(true);
        setIsInView(true);
      }
    };

    initializeImage();

    return () => {
      mounted = false;
    };
  }, [src]);

  // Intersection Observer for lazy loading (only for non-cached images)
  useEffect(() => {
    if (imageLoaded) return; // Skip if already loaded from cache

    const currentRef = containerRef.current;
    
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
  }, [imageLoaded]);

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

  // Force refresh on hover (fallback for stuck placeholders)
  const handleMouseEnter = () => {
    if (!imageLoaded && !imageError && isInView) {
      // Force a state refresh
      const img = imgRef.current;
      if (img && img.complete && img.naturalWidth > 0) {
        setImageLoaded(true);
      }
    }
  };

  const showPlaceholder = !imageLoaded && !imageError;

  return (
    <div 
      ref={containerRef}
      className={cn("relative overflow-hidden", className)}
      style={{
        width: width || '100%',
        height: height || '100%',
      }}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
    >
      {/* Placeholder */}
      {showPlaceholder && (
        <div className={cn(
          "absolute inset-0 bg-gray-200 dark:bg-gray-800 flex items-center justify-center transition-opacity duration-300",
          imageLoaded ? "opacity-0 pointer-events-none" : "opacity-100"
        )}>
          <div className="text-gray-500 dark:text-gray-400 text-sm">
            Loading...
          </div>
        </div>
      )}

      {/* Actual Image */}
      {(isInView || imageLoaded) && (
        <img
          ref={imgRef}
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
