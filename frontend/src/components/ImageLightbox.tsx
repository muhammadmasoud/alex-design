import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ZoomIn, ZoomOut, Download, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ImageLightboxProps {
  isOpen: boolean;
  onClose: () => void;
  src: string;
  alt: string;
  title?: string;
}

export default function ImageLightbox({ isOpen, onClose, src, alt, title }: ImageLightboxProps) {
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });

  // Reset state when lightbox opens/closes
  useEffect(() => {
    if (isOpen) {
      setScale(1);
      setRotation(0);
      setPosition({ x: 0, y: 0 });
      setLastPosition({ x: 0, y: 0 });
      setIsDragging(false);
    }
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
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyboard);
      document.body.style.overflow = 'unset';
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
        e.preventDefault();
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
      e.preventDefault();
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
      e.preventDefault();
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
        e.preventDefault();
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
      document.addEventListener('touchmove', handleGlobalTouchMove, { passive: false });
      document.addEventListener('touchend', handleGlobalTouchEnd);
    }

    return () => {
      document.removeEventListener('touchmove', handleGlobalTouchMove);
      document.removeEventListener('touchend', handleGlobalTouchEnd);
    };
  }, [isDragging, dragStart, scale]);

  const handleWheel = (e: React.WheelEvent) => {
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

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm"
        onClick={onClose}
      >
        {/* Controls */}
        <div className="absolute top-4 right-4 z-10 flex gap-2">
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
        <div className="absolute top-4 left-4 z-10 space-y-2">
          {title && (
            <h3 className="text-white text-lg font-semibold">{title}</h3>
          )}
          <div className="bg-black/50 text-white text-sm px-3 py-1 rounded-full backdrop-blur-sm">
            Zoom: {Math.round(scale * 100)}%
          </div>
        </div>

        {/* Image Container */}
        <div
          className="flex items-center justify-center h-full p-8"
          onClick={(e) => e.stopPropagation()}
          onWheel={handleWheel}
        >
          <motion.img
            src={src}
            alt={alt}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className={`max-w-full max-h-full object-contain select-none ${
              scale > 1 ? 'cursor-grab' : 'cursor-zoom-in'
            } ${isDragging ? 'cursor-grabbing' : ''}`}
            style={{
              transform: `scale(${scale}) translate(${position.x / scale}px, ${position.y / scale}px) rotate(${rotation}deg)`,
              transition: isDragging ? 'none' : 'transform 0.2s ease-out'
            }}
            onMouseDown={handleMouseDown}
            onTouchStart={handleTouchStart}
            onClick={(e) => {
              e.stopPropagation();
              if (scale === 1 && !isDragging) handleZoomIn();
            }}
            draggable={false}
          />
        </div>

        {/* Instructions */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
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
}
