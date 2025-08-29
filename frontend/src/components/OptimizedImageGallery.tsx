
// Optimized Image Component for React
import React, { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  lazy?: boolean;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  className = '',
  width,
  height,
  lazy = true
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  
  // Generate WebP version URL
  const getOptimizedSrc = (originalSrc: string) => {
    if (originalSrc.includes('.webp')) return originalSrc;
    
    const lastDot = originalSrc.lastIndexOf('.');
    if (lastDot === -1) return originalSrc;
    
    return originalSrc.substring(0, lastDot) + '.webp';
  };
  
  const webpSrc = getOptimizedSrc(src);
  
  return (
    <picture className={className}>
      {/* WebP version for better compression */}
      <source srcSet={webpSrc} type="image/webp" />
      
      {/* Fallback to original format */}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={lazy ? 'lazy' : 'eager'}
        onLoad={() => setImageLoaded(true)}
        onError={() => setImageError(true)}
        className={`transition-opacity duration-300 ${
          imageLoaded ? 'opacity-100' : 'opacity-0'
        } ${imageError ? 'hidden' : ''}`}
      />
      
      {/* Loading placeholder */}
      {!imageLoaded && !imageError && (
        <div 
          className="bg-gray-200 animate-pulse"
          style={{ width, height }}
        />
      )}
      
      {/* Error fallback */}
      {imageError && (
        <div 
          className="bg-gray-100 flex items-center justify-center text-gray-400"
          style={{ width, height }}
        >
          Image not available
        </div>
      )}
    </picture>
  );
};
