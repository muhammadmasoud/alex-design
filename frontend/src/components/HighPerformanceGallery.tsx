import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import ProgressiveImage from './ProgressiveImage';

interface ImageItem {
  id: number;
  src: string;
  alt: string;
  title?: string;
  description?: string;
  order: number;
}

interface HighPerformanceGalleryProps {
  images: ImageItem[];
  className?: string;
  itemClassName?: string;
  enableLightbox?: boolean;
  onImageClick?: (image: ImageItem) => void;
  priorityCount?: number;
  lazyLoadThreshold?: number;
  virtualScrolling?: boolean;
  maxVisibleItems?: number;
}

export default function HighPerformanceGallery({
  images,
  className,
  itemClassName,
  enableLightbox = false,
  onImageClick,
  priorityCount = 6,
  lazyLoadThreshold = 100,
  virtualScrolling = true,
  maxVisibleItems = 20,
}: HighPerformanceGalleryProps) {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: priorityCount });
  const [isIntersecting, setIsIntersecting] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Sort images by order
  const sortedImages = useMemo(() => {
    return [...images].sort((a, b) => a.order - b.order);
  }, [images]);

  // Separate priority and lazy images
  const priorityImages = useMemo(() => {
    return sortedImages.slice(0, priorityCount);
  }, [sortedImages, priorityCount]);

  const lazyImages = useMemo(() => {
    return sortedImages.slice(priorityCount);
  }, [sortedImages, priorityCount]);

  // Virtual scrolling: only render visible images + buffer
  const visibleImages = useMemo(() => {
    if (!virtualScrolling) return sortedImages;
    
    const buffer = Math.ceil(maxVisibleItems * 0.2); // 20% buffer
    const start = Math.max(0, visibleRange.start - buffer);
    const end = Math.min(sortedImages.length, visibleRange.end + buffer);
    
    return sortedImages.slice(start, end);
  }, [sortedImages, visibleRange, virtualScrolling, maxVisibleItems]);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!virtualScrolling) return;

    const options = {
      root: null,
      rootMargin: `${lazyLoadThreshold}px`,
      threshold: 0.1,
    };

    observerRef.current = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          // Load more images when container comes into view
          setVisibleRange(prev => ({
            start: prev.start,
            end: Math.min(prev.end + 8, sortedImages.length)
          }));
        }
      });
    }, options);

    if (containerRef.current) {
      observerRef.current.observe(containerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [virtualScrolling, lazyLoadThreshold, sortedImages.length]);

  // Handle scroll to load more images
  const handleScroll = useCallback(() => {
    if (!virtualScrolling || !containerRef.current) return;

    const container = containerRef.current;
    const scrollTop = container.scrollTop;
    const containerHeight = container.clientHeight;
    const scrollHeight = container.scrollHeight;

    // Load more images when user scrolls near bottom
    if (scrollTop + containerHeight >= scrollHeight - 200) {
      setVisibleRange(prev => ({
        start: prev.start,
        end: Math.min(prev.end + 6, sortedImages.length)
      }));
    }
  }, [virtualScrolling, sortedImages.length]);

  useEffect(() => {
    const container = containerRef.current;
    if (container && virtualScrolling) {
      container.addEventListener('scroll', handleScroll, { passive: true });
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll, virtualScrolling]);

  const handleImageClick = useCallback((image: ImageItem) => {
    if (enableLightbox || onImageClick) {
      onImageClick?.(image);
    }
  }, [enableLightbox, onImageClick]);

  // Loading skeleton for lazy images
  const LoadingSkeleton = () => (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="aspect-square bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse rounded-lg" />
      ))}
    </div>
  );

  return (
    <div className={cn("space-y-6", className)}>
      {/* Priority Images - Load immediately */}
      {priorityImages.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <AnimatePresence>
            {priorityImages.map((image, index) => (
              <motion.div
                key={image.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ 
                  duration: 0.4, 
                  delay: index * 0.1,
                  ease: "easeOut"
                }}
                className={cn("aspect-square", itemClassName)}
              >
                <ProgressiveImage
                  src={image.src}
                  alt={image.alt}
                  priority={true}
                  className="w-full h-full rounded-lg"
                  enableLightbox={enableLightbox}
                  onClick={() => handleImageClick(image)}
                />
                {image.title && (
                  <p className="mt-2 text-sm font-medium text-center text-gray-700 dark:text-gray-300">
                    {image.title}
                  </p>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Lazy Images - Load progressively */}
      {lazyImages.length > 0 && (
        <div 
          ref={containerRef}
          className="max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600"
        >
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <AnimatePresence>
              {visibleImages.slice(priorityCount).map((image, index) => (
                <motion.div
                  key={image.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ 
                    duration: 0.3, 
                    delay: (index % 6) * 0.05,
                    ease: "easeOut"
                  }}
                  className={cn("aspect-square", itemClassName)}
                >
                  <ProgressiveImage
                    src={image.src}
                    alt={image.alt}
                    priority={false}
                    className="w-full h-full rounded-lg"
                    enableLightbox={enableLightbox}
                    onClick={() => handleImageClick(image)}
                  />
                  {image.title && (
                    <p className="mt-2 text-sm font-medium text-center text-gray-700 dark:text-gray-300">
                      {image.title}
                    </p>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Show loading indicator when more images are being loaded */}
          {visibleRange.end < sortedImages.length && (
            <div className="flex justify-center py-6">
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm">Loading more images...</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {sortedImages.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-gray-500 dark:text-gray-400">No images available</p>
        </div>
      )}
    </div>
  );
}
