import { lazy, Suspense, useEffect, useState } from "react";
import { motion } from "framer-motion";
import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Building2, Palette, ArrowUp } from "lucide-react";
import { containerVariants, itemVariants } from "@/components/PageTransition";

// Lazy load components for better performance
const CategorySection = lazy(() => import("@/components/CategorySection"));

export default function ProjectsPage() {
  const [activeSection, setActiveSection] = useState<'architecture' | 'interior'>('architecture');
  const [showScrollTop, setShowScrollTop] = useState(false);

  // Handle scroll detection for active section and show scroll top button
  useEffect(() => {
    const handleScroll = () => {
      const architectureSection = document.getElementById('architecture-design');
      const interiorSection = document.getElementById('interior-design');
      const scrollY = window.scrollY;
      
      // Show scroll to top button after scrolling 300px
      setShowScrollTop(scrollY > 300);
      
      if (architectureSection && interiorSection) {
        const architectureTop = architectureSection.offsetTop - 100;
        const interiorTop = interiorSection.offsetTop - 100;
        
        if (scrollY >= interiorTop) {
          setActiveSection('interior');
        } else if (scrollY >= architectureTop) {
          setActiveSection('architecture');
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <motion.div 
      className="container py-8 sm:py-10 px-4 sm:px-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO 
        title="Architecture & Interior Design Projects | Alexandria Design Portfolio" 
        description="Explore our portfolio of architecture and interior design projects in Egypt. Modern residential homes, commercial buildings, and innovative design solutions by Alexandria Design studio."
        canonical="/projects"
        keywords="architecture projects Egypt, interior design projects, residential architecture, commercial buildings, modern architecture portfolio, Alexandria Design projects, sustainable buildings"
        structuredData={{
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          "name": "Architecture & Interior Design Projects Portfolio",
          "description": "Portfolio of architecture and interior design projects by Alexandria Design",
          "mainEntity": {
            "@type": "ItemList",
            "name": "Design Projects",
            "description": "Collection of architecture and interior design projects showcasing residential, commercial, and innovative design solutions"
          }
        }}
      />
      
      <motion.header className="mb-8" variants={itemVariants}>
        <h1 className="font-heading text-2xl sm:text-3xl mb-2">Projects Portfolio</h1>
        <p className="text-sm sm:text-base text-muted-foreground mb-6">
          Explore our comprehensive portfolio featuring both architectural design and interior design projects. 
          Each section includes its own search, filtering, and pagination capabilities.
        </p>
        
        {/* Navigation buttons */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 p-4 bg-background/95 backdrop-blur-sm rounded-lg border">
          <Button
            onClick={() => document.getElementById('architecture-design')?.scrollIntoView({ behavior: 'smooth' })}
            className={`flex items-center gap-2 transition-all ${
              activeSection === 'architecture' 
                ? 'bg-primary hover:bg-primary/90 text-primary-foreground shadow-md' 
                : 'bg-muted hover:bg-muted/80 text-muted-foreground'
            }`}
          >
            <Building2 size={18} />
            Architecture Design
          </Button>
          <Button
            onClick={() => document.getElementById('interior-design')?.scrollIntoView({ behavior: 'smooth' })}
            className={`flex items-center gap-2 transition-all ${
              activeSection === 'interior' 
                ? 'bg-primary hover:bg-primary/90 text-primary-foreground shadow-md' 
                : 'bg-muted hover:bg-muted/80 text-muted-foreground'
            }`}
          >
            <Palette size={18} />
            Interior Design
          </Button>
        </div>
      </motion.header>

      {/* Architecture Design Section Header */}
      <motion.div 
        className="relative mb-8 mt-12 text-center"
        variants={itemVariants}
      >
        <div className="flex items-center justify-center gap-2 mb-4">
          <Building2 size={24} className="text-primary" />
          <h2 className="font-heading text-xl sm:text-2xl font-semibold">Architecture Design</h2>
        </div>
        <p className="text-sm sm:text-base text-muted-foreground max-w-md mx-auto">
          Browse our architectural projects including residential, commercial, and innovative building designs.
        </p>
      </motion.div>

      {/* Architecture Design Section */}
      <Suspense fallback={<div className="text-center py-8">Loading Architecture Design projects...</div>}>
        <CategorySection
          sectionId="architecture-design"
          categoryName="Architecture Design"
          displayTitle=""
          description=""
        />
      </Suspense>

      {/* Decorative Divider - Same as Home Page */}
      <motion.section className="py-8 sm:py-12 md:py-16" variants={itemVariants}>
        <div className="container px-3 sm:px-6">
          <motion.div 
            className="relative flex items-center justify-center"
            variants={itemVariants}
            whileInView={{ opacity: 1, scale: 1 }}
            initial={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            {/* Outer glow effect */}
            <div className="absolute inset-0 flex items-center">
              <div className="w-full h-px bg-gradient-to-r from-transparent via-primary/10 to-transparent blur-sm"></div>
            </div>
            
            {/* Main decorative line */}
            <div className="absolute inset-0 flex items-center">
              <div className="w-full h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
            </div>
            
            {/* Secondary accent line */}
            <div className="absolute inset-0 flex items-center">
              <div className="w-full h-px bg-gradient-to-r from-transparent via-accent/15 to-transparent" style={{ transform: 'translateY(1px)' }}></div>
            </div>
            
            {/* Center ornamental design */}
            <div className="relative bg-background px-8 py-2">
              <div className="flex items-center justify-center gap-4">
                {/* Left ornamental pattern */}
                <motion.div 
                  className="flex items-center gap-1.5"
                  initial={{ x: -20, opacity: 0 }}
                  whileInView={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3, duration: 0.6 }}
                >
                  <div className="w-1 h-1 rounded-full bg-primary/60 animate-pulse"></div>
                  <div className="w-2 h-2 rounded-full bg-primary/40 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-accent/50 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </motion.div>
                
                {/* Central diamond ornament */}
                <motion.div 
                  className="relative"
                  initial={{ rotate: 45, scale: 0 }}
                  whileInView={{ rotate: 0, scale: 1 }}
                  transition={{ delay: 0.5, duration: 0.8, ease: "easeOut" }}
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/20 flex items-center justify-center shadow-lg">
                    <div className="w-4 h-4 rounded-md bg-gradient-to-br from-primary/30 to-accent/30 relative">
                      <div className="absolute inset-0.5 rounded-sm bg-gradient-to-br from-primary/60 to-accent/60 animate-pulse"></div>
                    </div>
                  </div>
                </motion.div>
                
                {/* Right ornamental pattern */}
                <motion.div 
                  className="flex items-center gap-1.5"
                  initial={{ x: 20, opacity: 0 }}
                  whileInView={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3, duration: 0.6 }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-accent/50 animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                  <div className="w-2 h-2 rounded-full bg-primary/40 animate-pulse" style={{ animationDelay: '0.8s' }}></div>
                  <div className="w-1 h-1 rounded-full bg-primary/60 animate-pulse" style={{ animationDelay: '1s' }}></div>
                </motion.div>
              </div>
              
              {/* Subtle text decoration */}
              <motion.div 
                className="text-center mt-2"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7, duration: 0.5 }}
              >
                <span className="text-xs text-muted-foreground/60 font-light tracking-wider">
                  ◦ ◦ ◦
                </span>
              </motion.div>
            </div>
            
            {/* Animated sparkle effects */}
            <motion.div 
              className="absolute left-1/4 top-1/2 w-1 h-1 bg-accent/60 rounded-full"
              animate={{ 
                scale: [0, 1, 0],
                opacity: [0, 1, 0]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                delay: 0.5
              }}
            />
            <motion.div 
              className="absolute right-1/4 top-1/2 w-1 h-1 bg-primary/60 rounded-full"
              animate={{ 
                scale: [0, 1, 0],
                opacity: [0, 1, 0]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                delay: 1.5
              }}
            />
          </motion.div>
        </div>
      </motion.section>

      {/* Interior Design Section Header */}
      <motion.div 
        className="relative mb-8 text-center"
        variants={itemVariants}
      >
        <div className="flex items-center justify-center gap-2 mb-4">
          <Palette size={24} className="text-primary" />
          <h2 className="font-heading text-xl sm:text-2xl font-semibold">Interior Design</h2>
        </div>
        <p className="text-sm sm:text-base text-muted-foreground max-w-md mx-auto">
          Discover our interior design projects featuring modern, luxurious, and functional space solutions.
        </p>
      </motion.div>

      {/* Interior Design Section */}
      <Suspense fallback={<div className="text-center py-8">Loading Interior Design projects...</div>}>
        <CategorySection
          sectionId="interior-design"
          categoryName="Interior Design"
          displayTitle=""
          description=""
        />
      </Suspense>

      {/* Scroll to top button */}
      {showScrollTop && (
        <Button
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 z-50 rounded-full w-12 h-12 p-0 shadow-lg"
          size="sm"
        >
          <ArrowUp size={20} />
        </Button>
      )}
    </motion.div>
  );
}
