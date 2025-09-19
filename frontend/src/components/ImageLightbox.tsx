import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { X, ZoomIn, ZoomOut, Download, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ImageLightboxProps {
  isOpen: boolean;
  onClose: () => void;
  src: string;
  alt: string;
  title?: string;
  loading?: boolean;
  optimizedSrc?: string; // Show optimized first, then swap to original
}

export default function ImageLightbox({ isOpen, onClose, src, alt, title, loading = false, optimizedSrc }: ImageLightboxProps) {
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });
  const [currentSrc, setCurrentSrc] = useState(optimizedSrc || src);
  const [originalLoaded, setOriginalLoaded] = useState(false);
  const [showingOptimized, setShowingOptimized] = useState(!!optimizedSrc);
  const imageContainerRef = useRef<HTMLDivElement>(null);

  // Progressive loading: start with optimized, load original in background
  useEffect(() => {
    if (isOpen && optimizedSrc && optimizedSrc !== src) {
      setCurrentSrc(optimizedSrc);
      setShowingOptimized(true);
      setOriginalLoaded(false);
      
      // Preload original image in background
      const img = new Image();
      img.onload = () => {
        setOriginalLoaded(true);
        // Auto-swap to original after it loads
        setTimeout(() => {
          setCurrentSrc(src);
          setShowingOptimized(false);
        }, 100);
      };
      img.src = src;
    } else {
      setCurrentSrc(src);
      setShowingOptimized(false);
    }
  }, [isOpen, src, optimizedSrc]);

  // Reset state when lightbox opens/closes and handle body scroll
  useEffect(() => {
    if (isOpen) {
      setScale(1);
      setRotation(0);
      setPosition({ x: 0, y: 0 });
      setLastPosition({ x: 0, y: 0 });
      setIsDragging(false);
      
      // Prevent body scroll when lightbox is open
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
    } else {
      // Restore body scroll when lightbox is closed
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    }

    // Cleanup on unmount
    return () => {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    };
  }, [isOpen]);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      if (!isOpen) return;
      
      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case '+':
        case '=':
          e.preventDefault();
          handleZoomIn();
          break;
        case '-':
          e.preventDefault();
          handleZoomOut();
          break;
        case 'r':
        case 'R':
          e.preventDefault();
          handleRotate();
          break;
        case '0':
          e.preventDefault();
          setScale(1);
          setPosition({ x: 0, y: 0 });
          setIsDragging(false);
          break;
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyboard);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyboard);
    };
  }, [isOpen, onClose, scale]);

  const handleZoomIn = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setScale(prev => Math.min(prev * 1.5, 4));
  };

  const handleZoomOut = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setScale(prev => Math.max(prev / 1.5, 0.5));
  };

  const handleRotate = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setRotation(prev => prev + 90);
  };

  const handleDownload = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const link = document.createElement('a');
    link.href = src;
    link.download = title || 'image';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Global mouse event handlers for smooth dragging
  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (isDragging && scale > 1) {
        // Remove preventDefault to avoid potential passive event listener issues
        const newX = e.clientX - dragStart.x;
        const newY = e.clientY - dragStart.y;
        setPosition({ x: newX, y: newY });
      }
    };

    const handleGlobalMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
      }
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleGlobalMouseMove);
      document.addEventListener('mouseup', handleGlobalMouseUp);
      document.body.style.userSelect = 'none'; // Prevent text selection while dragging
    }

    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove);
      document.removeEventListener('mouseup', handleGlobalMouseUp);
      document.body.style.userSelect = '';
    };
  }, [isDragging, dragStart, scale]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (scale > 1) {
      // Remove preventDefault to avoid potential passive event listener issues
      e.stopPropagation();
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  // Touch support for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    if (scale > 1 && e.touches.length === 1) {
      // Remove preventDefault to avoid passive event listener issues
      e.stopPropagation();
      setIsDragging(true);
      const touch = e.touches[0];
      setDragStart({
        x: touch.clientX - position.x,
        y: touch.clientY - position.y
      });
    }
  };

  // Global touch event handlers
  useEffect(() => {
    const handleGlobalTouchMove = (e: TouchEvent) => {
      if (isDragging && scale > 1 && e.touches.length === 1) {
        // Don't call preventDefault() to avoid passive listener issues
        // Instead, handle the touch movement without preventing default
        const touch = e.touches[0];
        const newX = touch.clientX - dragStart.x;
        const newY = touch.clientY - dragStart.y;
        setPosition({ x: newX, y: newY });
      }
    };

    const handleGlobalTouchEnd = () => {
      if (isDragging) {
        setIsDragging(false);
      }
    };

    if (isDragging) {
      // Remove passive: false to avoid the preventDefault error
      document.addEventListener('touchmove', handleGlobalTouchMove, { passive: true });
      document.addEventListener('touchend', handleGlobalTouchEnd, { passive: true });
    }

    return () => {
      document.removeEventListener('touchmove', handleGlobalTouchMove);
      document.removeEventListener('touchend', handleGlobalTouchEnd);
    };
  }, [isDragging, dragStart, scale]);

  // Handle wheel events manually to avoid passive listener issues
  useEffect(() => {
    const container = imageContainerRef.current;
    if (!container || !isOpen) return;

    const handleWheelEvent = (e: WheelEvent) => {
      e.preventDefault();
      e.stopPropagation();
      
      // More responsive zoom based on deltaY magnitude
      const zoomIntensity = 0.1;
      const wheel = e.deltaY < 0 ? 1 : -1;
      const zoom = Math.exp(wheel * zoomIntensity);
      const newScale = Math.min(Math.max(scale * zoom, 0.5), 4);
      
      setScale(newScale);
      
      // Reset position if zooming out to 1x or below
      if (newScale <= 1) {
        setPosition({ x: 0, y: 0 });
        setIsDragging(false);
      }
    };

    // Add wheel event listener with non-passive option
    container.addEventListener('wheel', handleWheelEvent, { passive: false });
    
    return () => {
      container.removeEventListener('wheel', handleWheelEvent);
    };
  }, [isOpen, scale]);

  if (!isOpen) return null;

  const lightboxContent = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[9999] bg-black/95 backdrop-blur-sm overflow-hidden"
        style={{
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          width: '100vw',
          height: '100vh',
          position: 'fixed'
        }}
        onClick={onClose}
      >
        {/* Controls */}
        <div className="absolute top-4 right-4 z-10 flex gap-2" onClick={(e) => e.stopPropagation()}>
          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => handleZoomIn(e)}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => handleZoomOut(e)}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => handleRotate(e)}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
            title="Rotate"
          >
            <RotateCw className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => handleDownload(e)}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
            title="Download"
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
            title="Close"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Title and Zoom Level */}
        <div className="absolute top-4 left-4 z-10 space-y-2" onClick={(e) => e.stopPropagation()}>
          {title && (
            <h3 className="text-white text-lg font-semibold">{title}</h3>
          )}
          <div className="bg-black/50 text-white text-sm px-3 py-1 rounded-full backdrop-blur-sm">
            Zoom: {Math.round(scale * 100)}%
          </div>
        </div>

        {/* Image Container */}
        <div
          className="flex items-center justify-center w-full h-full p-8"
          style={{
            width: '100vw',
            height: '100vh',
            position: 'relative',
            touchAction: 'none', // Prevent default touch actions
            userSelect: 'none'   // Prevent text selection
          }}
          onClick={onClose}
          ref={imageContainerRef}
        >
          {loading ? (
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              <p className="text-white text-sm">Loading original image...</p>
            </div>
          ) : (
            <div className="relative w-full h-full flex items-center justify-center">
              <motion.img
                src={currentSrc}
                alt={alt}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className={`max-w-full max-h-full object-contain select-none ${
                  scale > 1 ? 'cursor-grab' : 'cursor-zoom-in'
                } ${isDragging ? 'cursor-grabbing' : ''}`}
                style={{
                  transform: `scale(${scale}) translate(${position.x / scale}px, ${position.y / scale}px) rotate(${rotation}deg)`,
                  transition: isDragging ? 'none' : 'transform 0.2s ease-out',
                  touchAction: 'none', // Prevent default touch actions
                  userSelect: 'none'   // Prevent text selection
                }}
                onMouseDown={handleMouseDown}
                onTouchStart={handleTouchStart}
                onClick={(e) => {
                  e.stopPropagation();
                  // Only zoom in if we're not dragging and scale is 1
                  if (scale === 1 && !isDragging) handleZoomIn();
                }}
                draggable={false}
              />
              
              {/* Quality indicator */}
              {showingOptimized && originalLoaded && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute bottom-4 right-4 bg-green-500/80 text-white text-xs px-2 py-1 rounded backdrop-blur-sm"
                >
                  Upgraded to original quality ✨
                </motion.div>
              )}
              
              {showingOptimized && !originalLoaded && (
                <div className="absolute bottom-4 right-4 bg-blue-500/80 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
                  Loading full quality...
                </div>
              )}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10" onClick={(e) => e.stopPropagation()}>
          <div className="bg-black/50 text-white text-sm px-4 py-2 rounded-lg backdrop-blur-sm text-center">
            <p>
              {scale === 1 ? 'Click to zoom' : 'Drag to pan'} • Scroll to zoom
              {isDragging && ' • Dragging...'}
            </p>
            <p className="text-xs mt-1 opacity-75">+/- keys: zoom • R: rotate • 0: reset • ESC: close</p>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );

  // Render the lightbox in a portal to ensure it's at the top level
  return createPortal(lightboxContent, document.body);
}
