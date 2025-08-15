import { useState, useRef, useEffect } from 'react';
import { motion } from "framer-motion";
import { Expand } from "lucide-react";
import { cn } from '@/lib/utils';
import ImageLightbox from "./ImageLightbox";

interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  fallbackSrc?: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  threshold?: number;
  enableLightbox?: boolean;
  lightboxTitle?: string;
  showZoomIcon?: boolean;
}

export default function LazyImage({
  src,
  alt,
  fallbackSrc = '/placeholder.svg',
  className,
  loading = 'lazy',
  threshold = 0.1,
  enableLightbox = false,
  lightboxTitle,
  showZoomIcon = true,
  ...props
}: LazyImageProps) {
  const [imageSrc, setImageSrc] = useState<string>(loading === 'eager' ? src : '');
  const [imageLoaded, setImageLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (loading === 'eager') {
      setImageSrc(src);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setImageSrc(src);
          observer.disconnect();
        }
      },
      { threshold, rootMargin: '50px' }
    );

    const currentImg = imgRef.current;
    if (currentImg) {
      observer.observe(currentImg);
    }

    return () => {
      if (currentImg) {
        observer.unobserve(currentImg);
      }
    };
  }, [src, loading, threshold]);

  const handleLoad = () => {
    setImageLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    setImageSrc(fallbackSrc);
  };

  const handleImageClick = () => {
    if (enableLightbox) {
      setLightboxOpen(true);
    }
  };

  return (
    <>
      <div 
        className={cn(
          "relative overflow-hidden group",
          enableLightbox && "cursor-pointer",
          className
        )}
        onClick={handleImageClick}
      >
        {/* Placeholder/skeleton while loading */}
        {!imageLoaded && !hasError && (
          <div 
            className={cn(
              "absolute inset-0 bg-muted animate-pulse",
              "flex items-center justify-center text-muted-foreground"
            )}
          >
            <div className="w-8 h-8 border-2 border-current border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        
        <motion.img
          ref={imgRef}
          src={imageSrc}
          alt={alt}
          loading={loading}
          onLoad={handleLoad}
          onError={handleError}
          className={cn(
            "transition-all duration-300",
            imageLoaded ? "opacity-100" : "opacity-0",
            enableLightbox && "group-hover:scale-105",
            className
          )}
          whileHover={enableLightbox ? { scale: 1.02 } : undefined}
          {...(props as any)}
        />

        {/* Zoom overlay */}
        {enableLightbox && showZoomIcon && imageLoaded && (
          <motion.div
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            className="absolute inset-0 bg-black/20 flex items-center justify-center"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              whileHover={{ scale: 1 }}
              className="bg-white/90 dark:bg-black/90 rounded-full p-3 backdrop-blur-sm"
            >
              <Expand className="h-6 w-6 text-gray-700 dark:text-gray-300" />
            </motion.div>
          </motion.div>
        )}
      </div>

      {/* Lightbox */}
      {enableLightbox && (
        <ImageLightbox
          isOpen={lightboxOpen}
          onClose={() => setLightboxOpen(false)}
          src={src}
          alt={alt}
          title={lightboxTitle}
        />
      )}
    </>
  );
}
