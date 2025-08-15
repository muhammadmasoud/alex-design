import { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Move } from 'lucide-react';
import { cn } from '@/lib/utils';
import OptimizedImage from './OptimizedImage';

interface BeforeAfterSliderProps {
  beforeImage: string;
  afterImage: string;
  beforeAlt?: string;
  afterAlt?: string;
  className?: string;
  initialPosition?: number; // 0-100
  showLabels?: boolean;
  aspectRatio?: string;
  enableLightbox?: boolean;
  title?: string;
}

export default function BeforeAfterSlider({
  beforeImage,
  afterImage,
  beforeAlt = "Before",
  afterAlt = "After", 
  className,
  initialPosition = 50,
  showLabels = true,
  aspectRatio = "16/9",
  enableLightbox = false,
  title
}: BeforeAfterSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  }, [isDragging]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.touches[0].clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  }, [isDragging]);

  const handleClick = useCallback((e: React.MouseEvent) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  }, []);

  return (
    <div className={cn("relative overflow-hidden rounded-lg", className)}>
      <div
        ref={containerRef}
        className="relative select-none"
        style={{ aspectRatio }}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleMouseUp}
        onClick={handleClick}
      >
        {/* After Image (Background) */}
        <div className="absolute inset-0">
          <OptimizedImage
            src={afterImage}
            alt={afterAlt}
            className="w-full h-full object-cover"
            aspectRatio={aspectRatio}
            enableLightbox={enableLightbox}
            lightboxTitle={title ? `${title} - After` : afterAlt}
            loading="eager"
          />
          {showLabels && (
            <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              After
            </div>
          )}
        </div>

        {/* Before Image (Overlay with clip) */}
        <div 
          className="absolute inset-0 overflow-hidden"
          style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
        >
          <OptimizedImage
            src={beforeImage}
            alt={beforeAlt}
            className="w-full h-full object-cover"
            aspectRatio={aspectRatio}
            enableLightbox={enableLightbox}
            lightboxTitle={title ? `${title} - Before` : beforeAlt}
            loading="eager"
          />
          {showLabels && (
            <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              Before
            </div>
          )}
        </div>

        {/* Slider Handle */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white shadow-lg cursor-ew-resize"
          style={{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }}
        >
          {/* Handle Circle */}
          <motion.div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center cursor-grab active:cursor-grabbing"
            onMouseDown={handleMouseDown}
            onTouchStart={handleMouseDown}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            animate={{
              scale: isDragging ? 1.2 : 1,
            }}
          >
            <Move className="w-4 h-4 text-gray-600" />
          </motion.div>
          
          {/* Vertical line extensions */}
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0.5 h-8 bg-white"></div>
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0.5 h-8 bg-white"></div>
        </div>

        {/* Instruction overlay */}
        <motion.div
          initial={{ opacity: 1 }}
          animate={{ opacity: isDragging ? 0 : 1 }}
          className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 text-white text-sm px-3 py-2 rounded-full backdrop-blur-sm pointer-events-none"
        >
          <p>Drag to compare • Click to jump</p>
        </motion.div>
      </div>

      {/* Title */}
      {title && (
        <div className="mt-4 text-center">
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm text-muted-foreground">Interactive before & after comparison</p>
        </div>
      )}
    </div>
  );
}

// Preset configurations
export const BeforeAfterPresets = {
  renovation: {
    aspectRatio: "16/9",
    showLabels: true,
    enableLightbox: true,
    initialPosition: 50
  },
  
  landscaping: {
    aspectRatio: "4/3", 
    showLabels: true,
    enableLightbox: true,
    initialPosition: 40
  },
  
  interior: {
    aspectRatio: "3/2",
    showLabels: true,
    enableLightbox: true,
    initialPosition: 60
  }
};
