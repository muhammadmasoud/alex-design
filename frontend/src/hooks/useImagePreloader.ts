import { useEffect, useState } from 'react';

interface ImagePreloaderState {
  isLoaded: boolean;
  hasError: boolean;
  isLoading: boolean;
}

export function useImagePreloader(src: string | undefined): ImagePreloaderState {
  const [state, setState] = useState<ImagePreloaderState>({
    isLoaded: false,
    hasError: false,
    isLoading: false,
  });

  useEffect(() => {
    if (!src) {
      setState({ isLoaded: false, hasError: false, isLoading: false });
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, hasError: false }));

    const img = new Image();
    
    const handleLoad = () => {
      setState({ isLoaded: true, hasError: false, isLoading: false });
    };
    
    const handleError = () => {
      setState({ isLoaded: false, hasError: true, isLoading: false });
    };

    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);
    
    // Add cache headers for faster subsequent loads
    img.crossOrigin = 'anonymous';
    img.src = src;

    // Cleanup function
    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
    };
  }, [src]);

  return state;
}

/**
 * Hook to aggressively preload original images in the background
 */
export function useOriginalImagePreloader(images: Array<{original_image_url?: string, image?: string}>) {
  useEffect(() => {
    // Only preload if we have a reasonable number of images (don't overwhelm bandwidth)
    if (images.length > 10) return;
    
    const preloadPromises = images.slice(0, 3).map(img => {
      const originalUrl = img.original_image_url || img.image;
      if (!originalUrl) return Promise.resolve();
      
      return new Promise<void>((resolve) => {
        const image = new Image();
        image.onload = () => resolve();
        image.onerror = () => resolve(); // Don't fail the whole batch
        image.crossOrigin = 'anonymous';
        image.src = originalUrl;
      });
    });
    
    Promise.allSettled(preloadPromises);
  }, [images]);
}
