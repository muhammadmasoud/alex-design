import { lazy, Suspense } from "react";
import { motion } from "framer-motion";
import SEO from "@/components/SEO";
import { containerVariants, itemVariants } from "@/components/PageTransition";

// Lazy load components for better performance
const CategorySection = lazy(() => import("@/components/CategorySection"));

export default function ProjectsPage() {
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
        <p className="text-sm sm:text-base text-muted-foreground">
          Explore our comprehensive portfolio featuring both architectural design and interior design projects. 
          Each section includes its own search, filtering, and pagination capabilities.
        </p>
      </motion.header>

      {/* Architecture Design Section */}
      <Suspense fallback={<div className="text-center py-8">Loading Architecture Design projects...</div>}>
        <CategorySection
          categoryName="Architecture Design"
          displayTitle="Architecture Design"
          description="Browse our architectural projects including residential, commercial, and innovative building designs."
        />
      </Suspense>

      {/* Interior Design Section */}
      <Suspense fallback={<div className="text-center py-8">Loading Interior Design projects...</div>}>
        <CategorySection
          categoryName="Interior Design"
          displayTitle="Interior Design"
          description="Discover our interior design projects featuring modern, luxurious, and functional space solutions."
        />
      </Suspense>
    </motion.div>
  );
}
