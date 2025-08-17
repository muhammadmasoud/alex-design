import React, { useState } from 'react';
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

  const handleLoad = () => {
    setImageLoaded(true);
  };

  const handleError = (e: any) => {
    setImageError(true);
    if (onError) onError(e);
  };

  if (imageError) {
    return (
      <div className={cn("bg-gray-100 flex items-center justify-center", className)}>
        <span className="text-gray-500 text-sm">Failed to load</span>
      </div>
    );
  }

  return (
    <div className={cn("relative", className)} onClick={onClick}>
      {!imageLoaded && (
        <div className="absolute inset-0 bg-gray-200 flex items-center justify-center z-10">
          <span className="text-gray-500 text-sm">Loading...</span>
        </div>
      )}
      <img
        src={src}
        alt={alt}
        className="w-full h-full object-cover"
        style={{
          width: width || '100%',
          height: height || '100%',
          display: imageLoaded ? 'block' : 'none'
        }}
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  );
}
