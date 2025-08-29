import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { isApiImage, handleImageError } from '@/lib/imageUtils';

interface ProgressiveImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholderSrc?: string;
  width?: number;
  height?: number;
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
  enableLightbox?: boolean;
  onClick?: () => void;
}

export default function ProgressiveImage({
  src,
  alt,
  className,
  placeholderSrc = '/placeholder.svg',
  width,
  height,
  priority = false,
  onLoad,
  onError,
  enableLightbox = false,
  onClick,
}: ProgressiveImageProps) {
  
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentSrc, setCurrentSrc] = useState<string>(src);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (priority) {
      // Load high-quality image immediately for priority images
      setCurrentSrc(src);
    } else if (isApiImage(src)) {
      // For API images, load directly without trying to generate low-quality versions
      setCurrentSrc(src);
      
      // Preload the image
      const img = new Image();
      img.onload = () => {
        setIsLoaded(true);
        setIsLoading(false);
        onLoad?.();
      };
      img.onerror = () => {
        setHasError(true);
        setIsLoading(false);
        onError?.();
      };
      img.src = src;
    } else {
      // For non-API images, use the original logic
      setCurrentSrc(src);
      
      // Preload image
      const img = new Image();
      img.onload = () => {
        setIsLoaded(true);
        setIsLoading(false);
        onLoad?.();
      };
      img.onerror = () => {
        setHasError(true);
        setIsLoading(false);
        onError?.();
      };
      img.src = src;
    }
  }, [src, priority, onLoad, onError]);

  const handleClick = () => {
    if (enableLightbox || onClick) {
      onClick?.();
    }
  };

  const handleImageErrorEvent = (event: React.SyntheticEvent<HTMLImageElement, Event>) => {
    setHasError(true);
    setIsLoading(false);
    onError?.();
    
    // Use the utility function to handle the error
    handleImageError(event, placeholderSrc);
  };

  // If there's an error and we have a placeholder, show it
  if (hasError && placeholderSrc) {
    return (
      <div className={cn("relative overflow-hidden", className)}>
        <img
          src={placeholderSrc}
          alt={alt}
          width={width}
          height={height}
          className="w-full h-full object-cover"
        />
      </div>
    );
  }

  return (
    <div 
      className={cn("relative overflow-hidden", className)}
      onClick={handleClick}
    >
      {/* Loading Skeleton */}
      {isLoading && !isLoaded && (
        <motion.div
          className="absolute inset-0 bg-muted animate-pulse"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}

      {/* Main Image */}
      <AnimatePresence mode="wait">
        <motion.img
          key={currentSrc}
          ref={imgRef}
          src={currentSrc}
          alt={alt}
          width={width}
          height={height}
          className={cn(
            "w-full h-full object-cover transition-all duration-500",
            isLoaded ? "scale-100" : "scale-105"
          )}
          initial={{ opacity: 0, scale: 1.05 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          onLoad={() => {
            setIsLoaded(true);
            setIsLoading(false);
            onLoad?.();
          }}
          onError={handleImageErrorEvent}
          loading={priority ? "eager" : "lazy"}
          decoding="async"
        />
      </AnimatePresence>

      {/* Loading Progress Bar */}
      {isLoading && !hasError && (
        <motion.div
          initial={{ width: "0%" }}
          animate={{ width: isLoaded ? "100%" : "60%" }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="absolute bottom-0 left-0 h-1 bg-primary"
        />
      )}
    </div>
  );
}
