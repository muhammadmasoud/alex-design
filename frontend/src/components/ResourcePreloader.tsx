import { useEffect } from 'react';

interface ResourcePreloaderProps {
  images?: string[];
  fonts?: string[];
  scripts?: string[];
}

export default function ResourcePreloader({ 
  images = [], 
  fonts = [], 
  scripts = [] 
}: ResourcePreloaderProps) {
  useEffect(() => {
    // Use a small delay to ensure the DOM is ready and avoid preload warnings
    const timer = setTimeout(() => {
      // Preload critical images with better timing
      images.forEach((src) => {
        // Check if the image is already in the DOM or about to be used
        const existingImg = document.querySelector(`img[src="${src}"]`);
        if (!existingImg) {
          const link = document.createElement('link');
          link.rel = 'preload';
          link.as = 'image';
          link.href = src;
          // Add fetchpriority for better resource hinting
          link.setAttribute('fetchpriority', 'high');
          document.head.appendChild(link);
          
          // Remove the preload link after a reasonable time to avoid warnings
          setTimeout(() => {
            if (link.parentNode) {
              link.remove();
            }
          }, 5000); // Remove after 5 seconds
        }
      });

      // Preload fonts
      fonts.forEach((src) => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.type = 'font/woff2';
        link.crossOrigin = 'anonymous';
        link.href = src;
        document.head.appendChild(link);
      });

      // Preload scripts
      scripts.forEach((src) => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'script';
        link.href = src;
        document.head.appendChild(link);
      });
    }, 100); // Small delay to ensure DOM is ready

    // Cleanup function
    return () => {
      clearTimeout(timer);
      // Remove preload links when component unmounts
      const preloadLinks = document.querySelectorAll('link[rel="preload"]');
      preloadLinks.forEach((link) => {
        if (
          images.includes(link.getAttribute('href') || '') ||
          fonts.includes(link.getAttribute('href') || '') ||
          scripts.includes(link.getAttribute('href') || '')
        ) {
          link.remove();
        }
      });
    };
  }, [images, fonts, scripts]);

  return null; // This component doesn't render anything
}
