import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ProgressiveImageProps {
  src: string; // Original high-quality image
  optimizedSrc?: string; // Optimized version for initial load
  alt: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  showQualityIndicator?: boolean;
  placeholder?: string;
  onLoadComplete?: () => void;
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

export default function ProgressiveImage({
  src,
  optimizedSrc,
  alt,
  className = '',
  loading = 'lazy',
  showQualityIndicator = false,
  placeholder = '/placeholder.svg',
  onLoadComplete,
  onClick,
  style
}: ProgressiveImageProps) {
  const [currentSrc, setCurrentSrc] = useState(optimizedSrc || placeholder);
  const [originalLoaded, setOriginalLoaded] = useState(false);
  const [showingOptimized, setShowingOptimized] = useState(!!optimizedSrc);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Progressive loading strategy
  useEffect(() => {
    if (!src) return;

    // Step 1: Show optimized immediately if available
    if (optimizedSrc && optimizedSrc !== src) {
      setCurrentSrc(optimizedSrc);
      setShowingOptimized(true);
      setOriginalLoaded(false);

      // Step 2: Preload original in background
      const originalImg = new Image();
      originalImg.onload = () => {
        setOriginalLoaded(true);
        // Step 3: Seamless upgrade to original
        setTimeout(() => {
          setCurrentSrc(src);
          setShowingOptimized(false);
          onLoadComplete?.();
        }, 100);
      };
      originalImg.onerror = () => {
        // If original fails, stick with optimized
        console.warn('Failed to load original image, using optimized version');
      };
      originalImg.src = src;
    } else {
      // No optimized version, load original directly
      setCurrentSrc(src);
      setShowingOptimized(false);
    }
  }, [src, optimizedSrc, onLoadComplete]);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (loading === 'lazy' && imgRef.current) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement;
              if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
              }
              observer.unobserve(img);
            }
          });
        },
        { threshold: 0.1, rootMargin: '50px' }
      );

      observer.observe(imgRef.current);
      return () => observer.disconnect();
    }
  }, [loading]);

  const handleLoad = () => {
    setImageLoaded(true);
    if (!showingOptimized) {
      onLoadComplete?.();
    }
  };

  const handleError = () => {
    setHasError(true);
    if (currentSrc !== placeholder) {
      setCurrentSrc(placeholder);
    }
  };

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Main image */}
      <motion.img
        ref={imgRef}
        src={loading === 'lazy' && !imageLoaded ? undefined : currentSrc}
        data-src={loading === 'lazy' ? currentSrc : undefined}
        alt={alt}
        className={`
          w-full h-full object-cover transition-all duration-500
          ${imageLoaded ? 'opacity-100' : 'opacity-0'}
          ${hasError ? 'bg-gray-200' : ''}
        `}
        onLoad={handleLoad}
        onError={handleError}
        loading={loading}
        decoding="async"
        onClick={onClick}
        style={style}
      />

      {/* Loading shimmer */}
      {!imageLoaded && !hasError && (
        <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse" />
      )}

      {/* Quality upgrade indicator */}
      <AnimatePresence>
        {showQualityIndicator && showingOptimized && originalLoaded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -10 }}
            transition={{ duration: 0.3 }}
            className="absolute top-3 right-3 z-10"
          >
            <div className="bg-green-500/90 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm shadow-lg flex items-center gap-1">
              <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
              HD Quality
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading indicator for original */}
      {showingOptimized && !originalLoaded && showQualityIndicator && (
        <div className="absolute top-3 right-3 z-10">
          <div className="bg-blue-500/90 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm shadow-lg flex items-center gap-1">
            <div className="w-1.5 h-1.5 bg-white rounded-full animate-ping" />
            Loading HD...
          </div>
        </div>
      )}

      {/* Error state */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-gray-400 text-sm">Image not available</div>
        </div>
      )}
    </div>
  );
}
