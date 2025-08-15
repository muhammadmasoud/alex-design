import { motion } from "framer-motion";
import SEO from "@/components/SEO";
import { containerVariants, itemVariants } from "@/components/PageTransition";
import OptimizedImage, { ImagePresets } from "@/components/OptimizedImage";
import BeforeAfterSlider, { BeforeAfterPresets } from "@/components/BeforeAfterSlider";
import GalleryGrid from "@/components/GalleryGrid";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

// Sample gallery data
const sampleGalleryItems = [
  {
    id: "1",
    src: "/api/placeholder/600/400",
    alt: "Modern House Exterior",
    title: "Contemporary Villa",
    category: "Residential",
    description: "A stunning modern villa with clean lines and large windows.",
    featured: true
  },
  {
    id: "2", 
    src: "/api/placeholder/600/600",
    alt: "Office Building",
    title: "Corporate Headquarters",
    category: "Commercial",
    description: "Sleek office building with sustainable design elements."
  },
  {
    id: "3",
    src: "/api/placeholder/600/800",
    alt: "Interior Design",
    title: "Minimalist Living Room",
    category: "Interior",
    description: "Clean, minimalist interior with natural lighting."
  },
  {
    id: "4",
    src: "/api/placeholder/600/450",
    alt: "Garden Design",
    title: "Zen Garden",
    category: "Landscape",
    description: "Peaceful zen garden with water features."
  },
  {
    id: "5",
    src: "/api/placeholder/600/350",
    alt: "Kitchen Renovation",
    title: "Modern Kitchen",
    category: "Interior",
    description: "Spacious kitchen with high-end appliances."
  },
  {
    id: "6",
    src: "/api/placeholder/600/500",
    alt: "Apartment Complex",
    title: "Urban Apartments",
    category: "Residential",
    description: "Multi-story residential complex in city center."
  }
];

export default function GalleryDemo() {
  return (
    <motion.div
      className="container py-8 sm:py-10 px-4 sm:px-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO 
        title="Gallery Features Demo | Alex Designs" 
        description="Explore our advanced gallery and media features including lightbox, before/after comparisons, and interactive layouts." 
        canonical="/gallery-demo" 
      />

      {/* Header */}
      <motion.header className="mb-12 text-center" variants={itemVariants}>
        <h1 className="font-heading text-3xl sm:text-4xl mb-4">Advanced Gallery Features</h1>
        <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
          Experience our enhanced gallery and media capabilities including image lightbox, 
          before/after comparisons, optimized loading, and interactive layouts.
        </p>
      </motion.header>

      {/* Feature Sections */}
      <div className="space-y-16">
        
        {/* Image Lightbox Demo */}
        <motion.section variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-1 h-6 bg-primary rounded-full" />
                Image Lightbox & Zoom
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-muted-foreground">
                Click any image to open in full-screen lightbox with zoom, pan, rotate, and download features.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                <OptimizedImage
                  src="/api/placeholder/400/300"
                  alt="Hero Image Example"
                  className="rounded-lg"
                  lightboxTitle="Modern Architecture Hero"
                  {...ImagePresets.hero}
                />
                <OptimizedImage
                  src="/api/placeholder/400/400"
                  alt="Thumbnail Example"
                  className="rounded-lg"
                  lightboxTitle="Project Thumbnail"
                  {...ImagePresets.thumbnail}
                />
                <OptimizedImage
                  src="/api/placeholder/400/500"
                  alt="Portrait Example"
                  className="rounded-lg"
                  lightboxTitle="Portrait Layout"
                  {...ImagePresets.portrait}
                />
              </div>
            </CardContent>
          </Card>
        </motion.section>

        <Separator />

        {/* Before/After Slider Demo */}
        <motion.section variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-1 h-6 bg-secondary rounded-full" />
                Before & After Comparisons
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-muted-foreground">
                Interactive before/after sliders perfect for showcasing renovations, 
                transformations, and project progress.
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <BeforeAfterSlider
                  beforeImage="/api/placeholder/600/400"
                  afterImage="/api/placeholder/600/400" 
                  title="Kitchen Renovation"
                  beforeAlt="Kitchen Before Renovation"
                  afterAlt="Kitchen After Renovation"
                  enableLightbox={true}
                  {...BeforeAfterPresets.renovation}
                />
                
                <BeforeAfterSlider
                  beforeImage="/api/placeholder/600/450"
                  afterImage="/api/placeholder/600/450"
                  title="Landscape Design"
                  beforeAlt="Garden Before"
                  afterAlt="Garden After"
                  enableLightbox={true}
                  {...BeforeAfterPresets.landscaping}
                />
              </div>
            </CardContent>
          </Card>
        </motion.section>

        <Separator />

        {/* Gallery Grid Demo */}
        <motion.section variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-1 h-6 bg-accent rounded-full" />
                Interactive Gallery Grid
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-muted-foreground">
                Advanced gallery with filtering, multiple layout options (grid, masonry, list), 
                and interactive features.
              </p>
              
              <GalleryGrid
                items={sampleGalleryItems}
                enableFilter={true}
                enableLightbox={true}
                enableLayoutToggle={true}
                aspectRatio="4/3"
                columns={3}
              />
            </CardContent>
          </Card>
        </motion.section>

        {/* Features Summary */}
        <motion.section variants={itemVariants}>
          <Card className="bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-center">🎉 Gallery Features Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">🔍</span>
                  </div>
                  <h3 className="font-semibold">Image Lightbox</h3>
                  <p className="text-sm text-muted-foreground">Full-screen viewing with zoom, pan, rotate, and download</p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-secondary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <h3 className="font-semibold">Optimized Loading</h3>
                  <p className="text-sm text-muted-foreground">WebP support, lazy loading, and progressive enhancement</p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">🎛️</span>
                  </div>
                  <h3 className="font-semibold">Interactive Layouts</h3>
                  <p className="text-sm text-muted-foreground">Grid, masonry, list views with filtering and sorting</p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">📱</span>
                  </div>
                  <h3 className="font-semibold">Mobile Optimized</h3>
                  <p className="text-sm text-muted-foreground">Touch gestures, responsive design, and mobile-first approach</p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">⏱️</span>
                  </div>
                  <h3 className="font-semibold">Before/After</h3>
                  <p className="text-sm text-muted-foreground">Interactive sliders for showcasing transformations</p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-2xl">🎨</span>
                  </div>
                  <h3 className="font-semibold">Smooth Animations</h3>
                  <p className="text-sm text-muted-foreground">Framer Motion powered transitions and micro-interactions</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.section>
      </div>
    </motion.div>
  );
}
