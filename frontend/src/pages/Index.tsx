import hero from "@/assets/hero-architecture.jpg";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight, Play, Pause, Eye, Calendar } from "lucide-react";
import { api, endpoints, PaginatedResponse } from "@/lib/api";
import { Project } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import LazyImage from "@/components/LazyImage";
import { containerVariants, itemVariants } from "@/components/PageTransition";

const Index = () => {
  const navigate = useNavigate();
  
  // Architecture Design state
  const [architectureProjects, setArchitectureProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Interior Design state
  const [interiorProjects, setInteriorProjects] = useState<Project[]>([]);
  const [interiorLoading, setInteriorLoading] = useState(true);
  const [currentInteriorSlide, setCurrentInteriorSlide] = useState(0);
  const [isInteriorPlaying, setIsInteriorPlaying] = useState(true);
  const [interiorError, setInteriorError] = useState<string | null>(null);

  // Auto-slide functionality for Architecture Design
  useEffect(() => {
    if (!isPlaying || architectureProjects.length <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % architectureProjects.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(interval);
  }, [isPlaying, architectureProjects.length]);

  // Auto-slide functionality for Interior Design
  useEffect(() => {
    if (!isInteriorPlaying || interiorProjects.length <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentInteriorSlide((prev) => (prev + 1) % interiorProjects.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(interval);
  }, [isInteriorPlaying, interiorProjects.length]);

  // Navigation functions for Architecture Design
  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % architectureProjects.length);
  }, [architectureProjects.length]);

  const prevSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev - 1 + architectureProjects.length) % architectureProjects.length);
  }, [architectureProjects.length]);

  const togglePlayPause = useCallback(() => {
    setIsPlaying(prev => !prev);
  }, []);

  // Navigation functions for Interior Design
  const nextInteriorSlide = useCallback(() => {
    setCurrentInteriorSlide((prev) => (prev + 1) % interiorProjects.length);
  }, [interiorProjects.length]);

  const prevInteriorSlide = useCallback(() => {
    setCurrentInteriorSlide((prev) => (prev - 1 + interiorProjects.length) % interiorProjects.length);
  }, [interiorProjects.length]);

  const toggleInteriorPlayPause = useCallback(() => {
    setIsInteriorPlaying(prev => !prev);
  }, []);

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  };

  // Handle navigation to About page with scroll to top
  const handleLearnMoreClick = () => {
    navigate('/about');
    // Ensure scroll to top after navigation
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  };

  // Fetch architecture design projects
  useEffect(() => {
    const fetchArchitectureProjects = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const { data } = await api.get<PaginatedResponse<Project>>(endpoints.projects, {
          params: {
            category: "Architecture Design",
            page_size: 8, // Get 8 projects for variety
            _t: Date.now() // Cache busting
          }
        });
        
        const projects = data.results || [];
        
        if (projects.length > 0) {
          setArchitectureProjects(projects);
          setCurrentSlide(0);
        } else {
          setError("No architecture design projects found");
        }
      } catch (err: unknown) {
        setError("Failed to load architecture projects");
        setArchitectureProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchArchitectureProjects();
  }, []);

  // Fetch interior design projects
  useEffect(() => {
    const fetchInteriorProjects = async () => {
      try {
        setInteriorLoading(true);
        setInteriorError(null);
        
        const { data } = await api.get<PaginatedResponse<Project>>(endpoints.projects, {
          params: {
            category: "Interior Design",
            page_size: 8, // Get 8 projects for variety
            _t: Date.now() // Cache busting
          }
        });
        
        const projects = data.results || [];
        
        if (projects.length > 0) {
          setInteriorProjects(projects);
          setCurrentInteriorSlide(0);
        } else {
          setInteriorError("No interior design projects found");
        }
      } catch (err: unknown) {
        setInteriorError("Failed to load interior projects");
        setInteriorProjects([]);
      } finally {
        setInteriorLoading(false);
      }
    };

    fetchInteriorProjects();
  }, []);

  return (
    <motion.div 
      className=""
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO title="Studio Arc — Modern Architecture" description="Minimal, elegant portfolio of modern architecture: featured projects, services, and contact." canonical="/" />
      <section className="relative overflow-hidden animate-hero-entrance">
        <div className="relative h-[45vh] sm:h-[55vh] md:h-[65vh] lg:h-[70vh] w-full">
          {/* Main hero image with Ken Burns effect */}
          <img 
            src={hero} 
            alt="Modern architecture facade hero" 
            loading="eager"
            className="h-full w-full object-cover animate-hero-ken-burns" 
          />
          
          {/* Dynamic gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/10 to-transparent" />
          <div className="absolute inset-0 animate-hero-gradient-shift opacity-60" />
          
          {/* Enhanced floating geometric elements */}
          <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-primary/40 rounded-full animate-hero-float-dynamic" />
          <div className="absolute top-1/5 right-1/3 w-2 h-2 bg-accent/60 rounded-full animate-hero-pulse-glow" />
          <div className="absolute top-1/3 right-1/4 w-1.5 h-1.5 bg-secondary/50 rounded-full animate-hero-float-reverse" />
          <div className="absolute bottom-1/3 left-1/3 w-2.5 h-2.5 bg-accent/70 rounded-full animate-hero-float-slow" />
          <div className="absolute bottom-1/4 right-1/2 w-1 h-1 bg-primary/60 rounded-full animate-hero-spiral" />
          <div className="absolute top-1/2 left-1/5 w-1.5 h-1.5 bg-secondary/40 rounded-full animate-hero-float-delayed" />
          
          {/* Additional eye-catching elements */}
          <div className="absolute top-1/6 left-1/2 w-4 h-0.5 bg-accent/30 animate-hero-pulse-glow" />
          <div className="absolute bottom-1/5 left-1/4 w-0.5 h-4 bg-primary/40 animate-hero-float-dynamic" />
        </div>
        
        <motion.div className="container absolute inset-0 flex items-end pb-4 sm:pb-8 md:pb-12 px-3 sm:px-6" variants={itemVariants}>
          <div className="max-w-2xl w-full">
            <motion.h1 className="font-heading text-xl sm:text-3xl md:text-4xl lg:text-5xl leading-tight" variants={itemVariants}>
              Designing spaces with clarity and purpose.
            </motion.h1>
            <motion.p className="mt-2 sm:mt-3 md:mt-4 text-xs sm:text-sm md:text-base text-muted-foreground leading-relaxed" variants={itemVariants}>
              We create thoughtfully designed spaces that seamlessly blend form and function. From intimate residential homes to bold commercial structures and inspiring public spaces, our practice emphasizes sustainable design, natural light integration, and timeless minimalist aesthetics that enhance the human experience.
            </motion.p>
            <motion.div className="mt-3 sm:mt-4 md:mt-6 flex flex-col sm:flex-row gap-2 sm:gap-3" variants={itemVariants}>
              <Button className="w-full sm:w-auto text-sm" size="sm" asChild><Link to="/projects">Browse projects</Link></Button>
              <Button variant="secondary" className="w-full sm:w-auto text-sm" size="sm" asChild><Link to="/contact">Start a project</Link></Button>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* Architecture Design Projects Gallery */}
      <motion.section className="py-12 sm:py-16 md:py-20 bg-gradient-to-b from-background to-muted/20" variants={itemVariants}>
        <div className="container px-3 sm:px-6">
          <motion.header className="mb-8 sm:mb-12 text-center" variants={itemVariants}>
            <h2 className="font-heading text-2xl sm:text-3xl md:text-4xl mb-4 text-primary">
              Architecture Designs
            </h2>
            <p className="text-sm sm:text-base md:text-lg text-muted-foreground max-w-2xl mx-auto">
              Explore our latest architectural projects showcasing innovation and design excellence
            </p>
          </motion.header>

          {loading ? (
            <motion.div className="space-y-6" variants={itemVariants}>
              <div className="h-[400px] sm:h-[500px] md:h-[600px] bg-muted/30 rounded-lg animate-pulse" />
              <div className="flex gap-4 justify-center">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="w-16 h-16 bg-muted/30 rounded-lg animate-pulse" />
                ))}
              </div>
            </motion.div>
          ) : error || architectureProjects.length === 0 ? (
            <motion.div 
              className="text-center py-16 text-muted-foreground" 
              variants={itemVariants}
            >
              <p>{error || "No projects available"}</p>
              <Button variant="outline" className="mt-4" asChild>
                <Link to="/projects">Browse All Projects</Link>
              </Button>
            </motion.div>
          ) : (
            <motion.div className="space-y-6" variants={itemVariants}>
              {/* Main Image Display */}
              <div 
                className="relative group"
                onMouseEnter={() => setIsPlaying(false)}
                onMouseLeave={() => setIsPlaying(true)}
              >
                <div className="relative h-[400px] sm:h-[500px] md:h-[600px] overflow-hidden rounded-lg bg-black">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentSlide}
                      initial={{ opacity: 0, scale: 1.02 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.6, ease: "easeInOut" }}
                      className="absolute inset-0"
                    >
                      <LazyImage
                        src={architectureProjects[currentSlide].image || "/placeholder.svg"}
                        alt={architectureProjects[currentSlide].title}
                        className="h-full w-full object-cover"
                      />
                      
                      {/* Subtle overlay for text readability */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      
                      {/* Project Info - Bottom Left */}
                      <motion.div 
                        className="absolute bottom-6 left-6 right-6 text-white"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                          <div className="max-w-2xl">
                            <h3 className="font-heading text-xl sm:text-2xl md:text-3xl mb-2 leading-tight">
                              {architectureProjects[currentSlide].title}
                            </h3>
                            <p className="text-white/90 text-sm sm:text-base line-clamp-2 mb-3">
                              {architectureProjects[currentSlide].description}
                            </p>
                            
                            {/* Categories and Date */}
                            <div className="flex flex-wrap items-center gap-2">
                              {architectureProjects[currentSlide].category_names?.slice(0, 2).map((category, index) => (
                                <Badge key={index} variant="secondary" className="bg-white/20 text-white border-white/30 backdrop-blur-sm text-xs">
                                  {category}
                                </Badge>
                              ))}
                              <span className="text-white/70 text-xs">
                                {formatDate(architectureProjects[currentSlide].project_date)}
                              </span>
                            </div>
                          </div>
                          
                          <Button 
                            asChild 
                            variant="secondary" 
                            className="w-fit bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20 hover:text-white transition-all duration-300"
                          >
                            <Link to={`/projects/${architectureProjects[currentSlide].id}`} className="flex items-center gap-2">
                              <Eye className="h-4 w-4" />
                              View Project
                            </Link>
                          </Button>
                        </div>
                      </motion.div>
                    </motion.div>
                  </AnimatePresence>
                </div>

                {/* Navigation Arrows - Only visible on hover */}
                <div className="absolute inset-y-0 left-0 right-0 flex items-center justify-between px-6 pointer-events-none">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={prevSlide}
                    className="pointer-events-auto bg-black/20 backdrop-blur-sm border-white/10 text-white hover:bg-black/40 hover:text-white opacity-0 group-hover:opacity-100 transition-all duration-300 h-12 w-12"
                    disabled={architectureProjects.length <= 1}
                  >
                    <ChevronLeft className="h-6 w-6" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={nextSlide}
                    className="pointer-events-auto bg-black/20 backdrop-blur-sm border-white/10 text-white hover:bg-black/40 hover:text-white opacity-0 group-hover:opacity-100 transition-all duration-300 h-12 w-12"
                    disabled={architectureProjects.length <= 1}
                  >
                    <ChevronRight className="h-6 w-6" />
                  </Button>
                </div>
              </div>

              {/* Thumbnail Navigation */}
              <div className="flex justify-center">
                <div className="flex gap-3 overflow-x-auto pb-2 max-w-full">
                  {architectureProjects.map((project, index) => (
                    <motion.button
                      key={project.id}
                      onClick={() => setCurrentSlide(index)}
                      className={`relative flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 rounded-lg overflow-hidden transition-all duration-300 ${
                        index === currentSlide 
                          ? 'ring-2 ring-primary ring-offset-2 ring-offset-background scale-105' 
                          : 'hover:scale-105 hover:ring-1 hover:ring-primary/50 hover:ring-offset-1 hover:ring-offset-background opacity-70 hover:opacity-100'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <LazyImage
                        src={project.image || "/placeholder.svg"}
                        alt={project.title}
                        className="h-full w-full object-cover"
                      />
                      
                      {/* Active indicator */}
                      {index === currentSlide && (
                        <motion.div
                          className="absolute inset-0 bg-primary/20 flex items-center justify-center"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        >
                          <div className="w-2 h-2 bg-white rounded-full" />
                        </motion.div>
                      )}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Play/Pause Controls */}
              <div className="flex justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={togglePlayPause}
                  className="gap-2"
                  disabled={architectureProjects.length <= 1}
                >
                  {isPlaying ? (
                    <>
                      <Pause className="h-4 w-4" />
                      Pause Slideshow
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Play Slideshow
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <motion.div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4" variants={itemVariants}>
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link to="/projects?category=Architecture%20Design">
                View All Architecture Projects
              </Link>
            </Button>
            <Button variant="outline" asChild size="lg" className="w-full sm:w-auto">
              <Link to="/contact">
                Start Your Project
              </Link>
            </Button>
          </motion.div>
        </div>
      </motion.section>

      {/* Decorative Divider */}
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

      {/* Interior Design Projects Gallery */}
      <motion.section className="py-12 sm:py-16 md:py-20 bg-gradient-to-b from-muted/20 to-background" variants={itemVariants}>
        <div className="container px-3 sm:px-6">
          <motion.header className="mb-8 sm:mb-12 text-center" variants={itemVariants}>
            <h2 className="font-heading text-2xl sm:text-3xl md:text-4xl mb-4 text-primary">
              Interior Designs
            </h2>
            <p className="text-sm sm:text-base md:text-lg text-muted-foreground max-w-2xl mx-auto">
              Discover our stunning interior design projects that transform spaces into beautiful, functional environments
            </p>
          </motion.header>

          {interiorLoading ? (
            <motion.div className="space-y-6" variants={itemVariants}>
              <div className="h-[400px] sm:h-[500px] md:h-[600px] bg-muted/30 rounded-lg animate-pulse" />
              <div className="flex gap-4 justify-center">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="w-16 h-16 bg-muted/30 rounded-lg animate-pulse" />
                ))}
              </div>
            </motion.div>
          ) : interiorError || interiorProjects.length === 0 ? (
            <motion.div 
              className="text-center py-16 text-muted-foreground" 
              variants={itemVariants}
            >
              <p>{interiorError || "No interior projects available"}</p>
              <Button variant="outline" className="mt-4" asChild>
                <Link to="/projects">Browse All Projects</Link>
              </Button>
            </motion.div>
          ) : (
            <motion.div className="space-y-6" variants={itemVariants}>
              {/* Main Image Display */}
              <div 
                className="relative group"
                onMouseEnter={() => setIsInteriorPlaying(false)}
                onMouseLeave={() => setIsInteriorPlaying(true)}
              >
                <div className="relative h-[400px] sm:h-[500px] md:h-[600px] overflow-hidden rounded-lg bg-black">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentInteriorSlide}
                      initial={{ opacity: 0, scale: 1.02 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.6, ease: "easeInOut" }}
                      className="absolute inset-0"
                    >
                      <LazyImage
                        src={interiorProjects[currentInteriorSlide].image || "/placeholder.svg"}
                        alt={interiorProjects[currentInteriorSlide].title}
                        className="h-full w-full object-cover"
                      />
                      
                      {/* Subtle overlay for text readability */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      
                      {/* Project Info - Bottom Left */}
                      <motion.div 
                        className="absolute bottom-6 left-6 right-6 text-white"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                          <div className="max-w-2xl">
                            <h3 className="font-heading text-xl sm:text-2xl md:text-3xl mb-2 leading-tight">
                              {interiorProjects[currentInteriorSlide].title}
                            </h3>
                            <p className="text-white/90 text-sm sm:text-base line-clamp-2 mb-3">
                              {interiorProjects[currentInteriorSlide].description}
                            </p>
                            
                            {/* Categories and Date */}
                            <div className="flex flex-wrap items-center gap-2">
                              {interiorProjects[currentInteriorSlide].category_names?.slice(0, 2).map((category, index) => (
                                <Badge key={index} variant="secondary" className="bg-white/20 text-white border-white/30 backdrop-blur-sm text-xs">
                                  {category}
                                </Badge>
                              ))}
                              <span className="text-white/70 text-xs">
                                {formatDate(interiorProjects[currentInteriorSlide].project_date)}
                              </span>
                            </div>
                          </div>
                          
                          <Button 
                            asChild 
                            variant="secondary" 
                            className="w-fit bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20 hover:text-white transition-all duration-300"
                          >
                            <Link to={`/projects/${interiorProjects[currentInteriorSlide].id}`} className="flex items-center gap-2">
                              <Eye className="h-4 w-4" />
                              View Project
                            </Link>
                          </Button>
                        </div>
                      </motion.div>
                    </motion.div>
                  </AnimatePresence>
                </div>

                {/* Navigation Arrows - Only visible on hover */}
                <div className="absolute inset-y-0 left-0 right-0 flex items-center justify-between px-6 pointer-events-none">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={prevInteriorSlide}
                    className="pointer-events-auto bg-black/20 backdrop-blur-sm border-white/10 text-white hover:bg-black/40 hover:text-white opacity-0 group-hover:opacity-100 transition-all duration-300 h-12 w-12"
                    disabled={interiorProjects.length <= 1}
                  >
                    <ChevronLeft className="h-6 w-6" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={nextInteriorSlide}
                    className="pointer-events-auto bg-black/20 backdrop-blur-sm border-white/10 text-white hover:bg-black/40 hover:text-white opacity-0 group-hover:opacity-100 transition-all duration-300 h-12 w-12"
                    disabled={interiorProjects.length <= 1}
                  >
                    <ChevronRight className="h-6 w-6" />
                  </Button>
                </div>
              </div>

              {/* Thumbnail Navigation */}
              <div className="flex justify-center">
                <div className="flex gap-3 overflow-x-auto pb-2 max-w-full">
                  {interiorProjects.map((project, index) => (
                    <motion.button
                      key={project.id}
                      onClick={() => setCurrentInteriorSlide(index)}
                      className={`relative flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 rounded-lg overflow-hidden transition-all duration-300 ${
                        index === currentInteriorSlide 
                          ? 'ring-2 ring-primary ring-offset-2 ring-offset-background scale-105' 
                          : 'hover:scale-105 hover:ring-1 hover:ring-primary/50 hover:ring-offset-1 hover:ring-offset-background opacity-70 hover:opacity-100'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <LazyImage
                        src={project.image || "/placeholder.svg"}
                        alt={project.title}
                        className="h-full w-full object-cover"
                      />
                      
                      {/* Active indicator */}
                      {index === currentInteriorSlide && (
                        <motion.div
                          className="absolute inset-0 bg-primary/20 flex items-center justify-center"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        >
                          <div className="w-2 h-2 bg-white rounded-full" />
                        </motion.div>
                      )}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Play/Pause Controls */}
              <div className="flex justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleInteriorPlayPause}
                  className="gap-2"
                  disabled={interiorProjects.length <= 1}
                >
                  {isInteriorPlaying ? (
                    <>
                      <Pause className="h-4 w-4" />
                      Pause Slideshow
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Play Slideshow
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <motion.div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4" variants={itemVariants}>
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link to="/projects?category=Interior%20Design">
                View All Interior Projects
              </Link>
            </Button>
            <Button variant="outline" asChild size="lg" className="w-full sm:w-auto">
              <Link to="/contact">
                Start Your Project
              </Link>
            </Button>
          </motion.div>
        </div>
      </motion.section>

      {/* Decorative Divider */}
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

      {/* About Us Section */}
      <motion.section className="py-12 sm:py-16 md:py-20 bg-gradient-to-b from-background to-primary/5" variants={itemVariants}>
        <div className="container px-3 sm:px-6">
          <motion.header className="mb-8 sm:mb-12 text-center" variants={itemVariants}>
            <h2 className="font-heading text-2xl sm:text-3xl md:text-4xl mb-4 text-primary">
              About Us — Alexandria Design
            </h2>
            <p className="text-sm sm:text-base md:text-lg text-muted-foreground max-w-2xl mx-auto">
              Creating sustainable, functional, and inspiring environments that enhance lives through innovative architectural design.
            </p>
          </motion.header>

          {/* Our Vision Card */}
          <motion.div className="mb-12 sm:mb-16" variants={itemVariants}>
            <Card className="max-w-4xl mx-auto p-6 sm:p-8 md:p-10 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
              <CardContent className="text-center p-0">
                <h3 className="font-heading text-xl sm:text-2xl md:text-3xl mb-4 sm:mb-6 text-primary">Our Vision</h3>
                <p className="text-sm sm:text-base md:text-lg text-muted-foreground leading-relaxed">
                  At Alexandria Design, we believe architecture is more than just buildings—it's about creating sustainable, functional, and inspiring environments that enhance lives. From design concepts to execution, we integrate creativity with precision, ensuring every project reflects innovation, sustainability, and client needs.
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Action Buttons */}
          <motion.div className="flex flex-col sm:flex-row items-center justify-center gap-4" variants={itemVariants}>
            <Button onClick={handleLearnMoreClick} size="lg" className="w-full sm:w-auto">
              Learn More About Us
            </Button>
            <Button variant="outline" asChild size="lg" className="w-full sm:w-auto">
              <Link to="/contact">
                Work With Us
              </Link>
            </Button>
          </motion.div>
        </div>
      </motion.section>
    </motion.div>
  );
};

export default Index;
