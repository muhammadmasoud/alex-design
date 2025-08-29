import { useEffect, useRef } from 'react';

interface UseImagePreloadOptions {
  src: string;
  priority?: 'high' | 'low' | 'auto';
  timeout?: number;
}

export function useImagePreload({ 
  src, 
  priority = 'high', 
  timeout = 5000 
}: UseImagePreloadOptions) {
  const preloadLinkRef = useRef<HTMLLinkElement | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!src) return;

    // Check if the image is already in the DOM to avoid unnecessary preloading
    const existingImg = document.querySelector(`img[src="${src}"]`);
    if (existingImg) {
      return; // Image is already in the DOM, no need to preload
    }

    // Create preload link
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = src;
    
    if (priority === 'high') {
      link.setAttribute('fetchpriority', 'high');
    }
    
    document.head.appendChild(link);
    preloadLinkRef.current = link;

    // Set timeout to remove preload link if not used
    timeoutRef.current = setTimeout(() => {
      if (link.parentNode) {
        link.remove();
        preloadLinkRef.current = null;
      }
    }, timeout);

    // Clean up on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (link.parentNode) {
        link.remove();
      }
    };
  }, [src, priority, timeout]);

  // Function to mark image as used (call this when image is actually displayed)
  const markAsUsed = () => {
    if (preloadLinkRef.current && preloadLinkRef.current.parentNode) {
      preloadLinkRef.current.remove();
      preloadLinkRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  return { markAsUsed };
}
