import React, { useState, useEffect } from 'react';
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
  onError,
  onClick,
}: OptimizedImageProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    // Reset states when src changes
    setImageLoaded(false);
    setImageError(false);

    // Preload the image
    const img = new Image();
    
    img.onload = () => {
      setImageLoaded(true);
      setImageError(false);
    };
    
    img.onerror = () => {
      setImageError(true);
      setImageLoaded(false);
      if (onError) {
        onError(new Error('Failed to load image'));
      }
    };
    
    img.src = src;

    // Cleanup
    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src, onError]);

  if (imageError) {
    return (
      <div className={cn(
        "bg-gray-100 dark:bg-gray-900 flex items-center justify-center",
        className
      )}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <div className="text-sm">Image not available</div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("relative overflow-hidden", className)} onClick={onClick}>
      {/* Loading placeholder - only show if image hasn't loaded */}
      {!imageLoaded && (
        <div className="absolute inset-0 bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
          <div className="text-gray-500 dark:text-gray-400 text-sm">
            Loading...
          </div>
        </div>
      )}
      
      {/* Actual image */}
      <img
        src={src}
        alt={alt}
        className={cn(
          "w-full h-full object-cover transition-opacity duration-300",
          imageLoaded ? "opacity-100" : "opacity-0"
        )}
        style={{
          width: width || '100%',
          height: height || '100%',
        }}
        loading="lazy"
        decoding="async"
        onLoad={() => setImageLoaded(true)}
        onError={() => {
          setImageError(true);
          if (onError) onError(new Error('Image load failed'));
        }}
      />
    </div>
  );
}
