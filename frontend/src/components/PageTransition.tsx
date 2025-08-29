import { motion, AnimatePresence } from "framer-motion";
import { ReactNode } from "react";
import { useLocation } from "react-router-dom";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

// Reuse the same animation variants from ProjectDetail and ServiceDetail
const pageVariants = {
  initial: { 
    opacity: 0,
    y: 20,
    scale: 0.98
  },
  in: { 
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: [0.4, 0.0, 0.2, 1] as const,
      when: "beforeChildren" as const,
      staggerChildren: 0.1,
    }
  },
  out: { 
    opacity: 0,
    y: -20,
    scale: 0.98,
    transition: {
      duration: 0.4,
      ease: [0.4, 0.0, 0.6, 1] as const
    }
  }
};

// Content container variants for staggered animations
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.6,
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
    transition: { duration: 0.5 },
  },
};

// Image variants for consistent image animations
export const imageVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.7 },
  },
};

export default function PageTransition({ children, className }: PageTransitionProps) {
  const location = useLocation();

  return (
    <AnimatePresence mode="sync" initial={true}>
      <motion.div
        key={location.pathname}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        className={className}
        // Optimize performance for production
        style={{
          willChange: 'opacity, transform',
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

// Specialized loading transition component for production
export function LoadingPageTransition() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex items-center justify-center"
      style={{ willChange: 'opacity' }}
    >
      <motion.div 
        className="text-center space-y-4"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        <motion.div 
          className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        <motion.div 
          className="text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Loading...
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
