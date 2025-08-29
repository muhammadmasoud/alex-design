import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

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
  const [currentSrc, setCurrentSrc] = useState(placeholderSrc);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);

  // Generate low-quality placeholder URL
  const getLowQualitySrc = (originalSrc: string) => {
    if (!originalSrc || originalSrc === placeholderSrc) return placeholderSrc;
    
    // Add quality parameter for backend optimization
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + '_q30' + originalSrc.substring(lastDot);
  };

  useEffect(() => {
    if (priority) {
      // Load high-quality image immediately for priority images
      setCurrentSrc(src);
    } else {
      // Load low-quality first, then high-quality
      const lowQualitySrc = getLowQualitySrc(src);
      setCurrentSrc(lowQualitySrc);
      
      // Preload high-quality image
      const highQualityImg = new Image();
      highQualityImg.onload = () => {
        setCurrentSrc(src);
        setIsLoaded(true);
        setIsLoading(false);
        onLoad?.();
      };
      highQualityImg.onerror = () => {
        setHasError(true);
        setIsLoading(false);
        onError?.();
      };
      highQualityImg.src = src;
    }
  }, [src, priority, onLoad, onError]);

  const handleClick = () => {
    if (enableLightbox || onClick) {
      onClick?.();
    }
  };

  return (
    <div 
      className={cn(
        "relative overflow-hidden",
        enableLightbox && "cursor-pointer",
        className
      )}
      onClick={handleClick}
      style={{ width, height }}
    >
      {/* Loading Skeleton */}
      <AnimatePresence>
        {isLoading && !hasError && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse"
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error State */}
      {hasError && (
        <div className="absolute inset-0 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <div className="text-center text-gray-500 dark:text-gray-400">
            <div className="w-12 h-12 mx-auto mb-2 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-sm">Image unavailable</p>
          </div>
        </div>
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
            if (currentSrc === src) {
              setIsLoaded(true);
              setIsLoading(false);
              onLoad?.();
            }
          }}
          onError={() => {
            setHasError(true);
            setIsLoading(false);
            onError?.();
          }}
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
