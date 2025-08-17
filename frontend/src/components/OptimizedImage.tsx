import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  effect?: 'blur' | 'black-and-white' | 'opacity';
  placeholder?: string;
  onError?: (e: any) => void;
  onClick?: () => void;
}

export default function OptimizedImage({
  src,
  alt,
  className,
  width,
  height,
  effect = 'blur',
  placeholder = '/placeholder.svg',
  onError,
  onClick,
}: OptimizedImageProps) {
  const handleError = (e: any) => {
    if (onError) {
      onError(e);
    } else {
      // Default error handling
      const target = e.target as HTMLImageElement;
      target.src = placeholder;
    }
  };

  return (
    <LazyLoadImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      effect={effect}
      className={cn(className)}
      onError={handleError}
      onClick={onClick}
      placeholder={
        <div className={cn(
          "bg-muted animate-pulse flex items-center justify-center",
          className
        )}>
          <div className="text-muted-foreground text-sm">Loading...</div>
        </div>
      }
      // Additional performance optimizations
      loading="lazy"
      decoding="async"
    />
  );
}
