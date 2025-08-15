import hero from "@/assets/hero-architecture.jpg";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, endpoints } from "@/lib/api";
import { Project } from "@/types";
import ProjectCard from "@/components/ProjectCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Link } from "react-router-dom";
import { containerVariants, itemVariants } from "@/components/PageTransition";

const Index = () => {
  const [featured, setFeatured] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get(endpoints.projects, { 
          params: { 
            page_size: 3,
            _t: Date.now() // Add timestamp to prevent caching
          } 
        });
        // Take only the first 3 projects to ensure we show exactly 3
        const results = data.results || [];
        setFeatured(results.slice(0, 3));
      } catch {
        setFeatured([]);
      } finally {
        setLoading(false);
      }
    };
    load();
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
        <div className="relative h-[60vh] w-full">
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
        
        <motion.div className="container absolute inset-0 flex items-end pb-12" variants={itemVariants}>
          <div className="max-w-2xl">
            <motion.h1 className="font-heading text-4xl sm:text-5xl" variants={itemVariants}>
              Designing spaces with clarity and purpose.
            </motion.h1>
            <motion.p className="mt-3 text-muted-foreground" variants={itemVariants}>
              We create thoughtfully designed spaces that seamlessly blend form and function. From intimate residential homes to bold commercial structures and inspiring public spaces, our practice emphasizes sustainable design, natural light integration, and timeless minimalist aesthetics that enhance the human experience.
            </motion.p>
            <motion.div className="mt-6 flex gap-3" variants={itemVariants}>
              <Button asChild><Link to="/projects">Browse projects</Link></Button>
              <Button variant="secondary" asChild><Link to="/contact">Start a project</Link></Button>
            </motion.div>
          </div>
        </motion.div>
      </section>

      <motion.section className="container py-12" variants={itemVariants}>
        <motion.header className="mb-6 flex items-end justify-between" variants={itemVariants}>
          <div>
            <h2 className="font-heading text-2xl">Featured projects</h2>
            <p className="text-muted-foreground">A selection from our recent work.</p>
          </div>
          <Button variant="ghost" asChild><Link to="/projects">View all</Link></Button>
        </motion.header>
        {loading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-72 w-full" />
            ))}
          </div>
        ) : (
          <motion.div 
            className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
            variants={itemVariants}
          >
            {featured.map((p, index) => (
              <motion.div
                key={p.id}
                variants={itemVariants}
                transition={{ delay: index * 0.1 }}
              >
                <ProjectCard project={p} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </motion.section>
    </motion.div>
  );
};

export default Index;
