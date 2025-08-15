import { useState, useRef, useEffect } from 'react';
import { motion } from "framer-motion";
import { Expand, Download } from "lucide-react";
import { cn } from '@/lib/utils';
import ImageLightbox from "./ImageLightbox";

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  fallbackSrc?: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  threshold?: number;
  enableLightbox?: boolean;
  lightboxTitle?: string;
  showZoomIcon?: boolean;
  sizes?: string;
  quality?: 'low' | 'medium' | 'high';
  aspectRatio?: string;
  showDownload?: boolean;
}

export default function OptimizedImage({
  src,
  alt,
  fallbackSrc = '/placeholder.svg',
  className,
  loading = 'lazy',
  threshold = 0.1,
  enableLightbox = false,
  lightboxTitle,
  showZoomIcon = true,
  sizes,
  quality = 'medium',
  aspectRatio,
  showDownload = false,
  ...props
}: OptimizedImageProps) {
  const [imageSrc, setImageSrc] = useState<string>(loading === 'eager' ? src : '');
  const [imageLoaded, setImageLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Generate optimized image URLs
  const generateOptimizedUrls = (originalSrc: string) => {
    // If it's a placeholder or external URL, return as-is
    if (originalSrc.includes('placeholder.svg') || originalSrc.startsWith('http')) {
      return {
        webp: originalSrc,
        jpg: originalSrc,
        original: originalSrc
      };
    }

    // For local images, you would typically use a service like Cloudinary or ImageKit
    // For now, we'll return the original but this is where you'd add optimization
    return {
      webp: originalSrc, // In production, this would be optimized WebP
      jpg: originalSrc,  // In production, this would be optimized JPEG
      original: originalSrc
    };
  };

  const optimizedUrls = generateOptimizedUrls(src);

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

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = src;
    link.download = lightboxTitle || alt || 'image';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div 
        className={cn(
          "relative overflow-hidden group",
          enableLightbox && "cursor-pointer",
          aspectRatio && "relative",
          className
        )}
        style={aspectRatio ? { aspectRatio } : undefined}
        onClick={handleImageClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
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
        
        {/* Progressive image with WebP support */}
        <picture>
          <source srcSet={optimizedUrls.webp} type="image/webp" />
          <source srcSet={optimizedUrls.jpg} type="image/jpeg" />
          <motion.img
            ref={imgRef}
            src={imageSrc}
            alt={alt}
            loading={loading}
            sizes={sizes}
            onLoad={handleLoad}
            onError={handleError}
            className={cn(
              "transition-all duration-300 w-full h-full object-cover",
              imageLoaded ? "opacity-100" : "opacity-0",
              enableLightbox && "group-hover:scale-105",
              aspectRatio && "absolute inset-0"
            )}
            whileHover={enableLightbox ? { scale: 1.02 } : undefined}
            {...(props as any)}
          />
        </picture>

        {/* Overlay with controls */}
        {imageLoaded && (enableLightbox || showDownload) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute inset-0 bg-black/20 flex items-center justify-center gap-2"
          >
            {enableLightbox && showZoomIcon && (
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: isHovered ? 1 : 0.8 }}
                className="bg-white/90 dark:bg-black/90 rounded-full p-3 backdrop-blur-sm"
              >
                <Expand className="h-6 w-6 text-gray-700 dark:text-gray-300" />
              </motion.div>
            )}
            
            {showDownload && (
              <motion.button
                initial={{ scale: 0.8 }}
                animate={{ scale: isHovered ? 1 : 0.8 }}
                onClick={handleDownload}
                className="bg-white/90 dark:bg-black/90 rounded-full p-3 backdrop-blur-sm hover:bg-white dark:hover:bg-black transition-colors"
              >
                <Download className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </motion.button>
            )}
          </motion.div>
        )}

        {/* Image quality indicator */}
        {quality !== 'high' && imageLoaded && (
          <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
            {quality.toUpperCase()}
          </div>
        )}
      </div>

      {/* Lightbox */}
      {enableLightbox && (
        <ImageLightbox
          isOpen={lightboxOpen}
          onClose={() => setLightboxOpen(false)}
          src={optimizedUrls.original}
          alt={alt}
          title={lightboxTitle}
        />
      )}
    </>
  );
}

// Preset configurations for common use cases
export const ImagePresets = {
  hero: {
    aspectRatio: "16/9",
    quality: "high" as const,
    enableLightbox: true,
    showZoomIcon: true,
    sizes: "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  },
  
  thumbnail: {
    aspectRatio: "1/1",
    quality: "medium" as const,
    enableLightbox: true,
    showZoomIcon: true,
    sizes: "(max-width: 768px) 50vw, 25vw"
  },
  
  gallery: {
    aspectRatio: "4/3",
    quality: "high" as const,
    enableLightbox: true,
    showZoomIcon: true,
    showDownload: true,
    sizes: "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  },
  
  portrait: {
    aspectRatio: "3/4",
    quality: "high" as const,
    enableLightbox: true,
    showZoomIcon: true,
    sizes: "(max-width: 768px) 100vw, 50vw"
  }
};
