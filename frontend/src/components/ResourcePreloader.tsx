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
    // Preload critical images
    images.forEach((src) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
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

    // Cleanup function
    return () => {
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
