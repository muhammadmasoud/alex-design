import { motion, AnimatePresence } from "framer-motion";
import { ReactNode, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

// Very simple page variants to prevent blank pages
const pageVariants = {
  initial: { 
    opacity: 0
  },
  in: { 
    opacity: 1,
    transition: {
      duration: 0.2
    }
  },
  out: { 
    opacity: 0,
    transition: {
      duration: 0.1
    }
  }
};

// Content container variants for staggered animations
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.4,
      when: "beforeChildren" as const,
      staggerChildren: 0.1,
    },
  },
};

// Item variants for consistent child animations
export const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 },
  },
};

// Image variants for consistent image animations
export const imageVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5 },
  },
};

export default function PageTransition({ children, className }: PageTransitionProps) {
  const location = useLocation();
  const [isVisible, setIsVisible] = useState(true);

  // Scroll to top on route change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    }
  }, [location.pathname]);

  // Ensure content is always visible
  useEffect(() => {
    setIsVisible(true);
  }, [location.pathname]);

  // Fallback if animation fails
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100);

    return () => clearTimeout(timer);
  }, [location.pathname]);

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        className={className}
        onAnimationComplete={() => setIsVisible(true)}
        style={{
          opacity: isVisible ? 1 : 0,
          minHeight: '100vh'
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

// Higher-order component for wrapping pages with transitions
export function withPageTransition<T extends object>(
  Component: React.ComponentType<T>
) {
  return function TransitionWrappedComponent(props: T) {
    return (
      <PageTransition>
        <Component {...props} />
      </PageTransition>
    );
  };
}

// Simple loading transition component
export function LoadingPageTransition() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <div className="text-sm text-muted-foreground">
          Loading...
        </div>
      </div>
    </div>
  );
}
