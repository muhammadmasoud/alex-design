import { useState, useEffect, useCallback } from 'react';

interface ImagePerformanceMetrics {
  loadTime: number;
  imageSize: number;
  fromCache: boolean;
}

interface UseImagePerformanceOptions {
  onLoad?: (metrics: ImagePerformanceMetrics) => void;
  onError?: (error: Error) => void;
}

export const useImagePerformance = (src: string, options: UseImagePerformanceOptions = {}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [metrics, setMetrics] = useState<ImagePerformanceMetrics | null>(null);

  const handleLoad = useCallback((img: HTMLImageElement) => {
    const loadTime = performance.now();
    const entry = performance.getEntriesByName(src)[0] as PerformanceResourceTiming;
    
    const imageMetrics: ImagePerformanceMetrics = {
      loadTime: entry ? entry.duration : loadTime,
      imageSize: entry ? entry.transferSize || 0 : 0,
      fromCache: entry ? entry.transferSize === 0 : false,
    };

    setMetrics(imageMetrics);
    setLoading(false);
    options.onLoad?.(imageMetrics);
  }, [src, options]);

  const handleError = useCallback((err: Event) => {
    const error = new Error(`Failed to load image: ${src}`);
    setError(error);
    setLoading(false);
    options.onError?.(error);
  }, [src, options]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setMetrics(null);

    const img = new Image();
    img.onload = () => handleLoad(img);
    img.onerror = handleError;
    img.src = src;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src, handleLoad, handleError]);

  return { loading, error, metrics };
};

// Hook for batch image loading performance
export const useBatchImagePerformance = (urls: string[]) => {
  const [loadingCount, setLoadingCount] = useState(0);
  const [totalMetrics, setTotalMetrics] = useState<{
    totalLoadTime: number;
    totalSize: number;
    fromCacheCount: number;
    errorCount: number;
  }>({
    totalLoadTime: 0,
    totalSize: 0,
    fromCacheCount: 0,
    errorCount: 0,
  });

  useEffect(() => {
    setLoadingCount(urls.length);
    setTotalMetrics({
      totalLoadTime: 0,
      totalSize: 0,
      fromCacheCount: 0,
      errorCount: 0,
    });

    const promises = urls.map(url => {
      return new Promise<ImagePerformanceMetrics | null>((resolve) => {
        const img = new Image();
        const startTime = performance.now();

        img.onload = () => {
          const loadTime = performance.now() - startTime;
          const entry = performance.getEntriesByName(url)[0] as PerformanceResourceTiming;
          
          resolve({
            loadTime: entry ? entry.duration : loadTime,
            imageSize: entry ? entry.transferSize || 0 : 0,
            fromCache: entry ? entry.transferSize === 0 : false,
          });
        };

        img.onerror = () => {
          resolve(null);
        };

        img.src = url;
      });
    });

    Promise.allSettled(promises).then((results) => {
      let completedCount = 0;
      let newMetrics = {
        totalLoadTime: 0,
        totalSize: 0,
        fromCacheCount: 0,
        errorCount: 0,
      };

      results.forEach((result) => {
        if (result.status === 'fulfilled' && result.value) {
          const metrics = result.value;
          newMetrics.totalLoadTime += metrics.loadTime;
          newMetrics.totalSize += metrics.imageSize;
          if (metrics.fromCache) newMetrics.fromCacheCount++;
        } else {
          newMetrics.errorCount++;
        }
        completedCount++;
      });

      setLoadingCount(urls.length - completedCount);
      setTotalMetrics(newMetrics);
    });
  }, [urls]);

  return {
    loading: loadingCount > 0,
    loadingCount,
    ...totalMetrics,
    averageLoadTime: totalMetrics.totalLoadTime / Math.max(1, urls.length - totalMetrics.errorCount),
    cacheHitRate: (totalMetrics.fromCacheCount / Math.max(1, urls.length)) * 100,
  };
};
