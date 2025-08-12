import hero from "@/assets/hero-architecture.jpg";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import { useEffect, useState } from "react";
import { api, endpoints } from "@/lib/api";
import { Project } from "@/types";
import ProjectCard from "@/components/ProjectCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Link } from "react-router-dom";

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
    <div className="">
      <SEO title="Studio Arc — Modern Architecture" description="Minimal, elegant portfolio of modern architecture: featured projects, services, and contact." canonical="/" />
      <section className="relative">
        <img src={hero} alt="Modern architecture facade hero" className="h-[60vh] w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/10 to-transparent" />
        <div className="container absolute inset-0 flex items-end pb-12">
          <div className="max-w-2xl animate-enter">
            <h1 className="font-heading text-4xl sm:text-5xl">Designing spaces with clarity and purpose.</h1>
            <p className="mt-3 text-muted-foreground">Residential, commercial, and public architecture with a focus on minimalism and light.</p>
            <div className="mt-6 flex gap-3">
              <Button asChild><Link to="/projects">Browse projects</Link></Button>
              <Button variant="secondary" asChild><Link to="/contact">Start a project</Link></Button>
            </div>
          </div>
        </div>
      </section>

      <section className="container py-12">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <h2 className="font-heading text-2xl">Featured projects</h2>
            <p className="text-muted-foreground">A selection from our recent work.</p>
          </div>
          <Button variant="ghost" asChild><Link to="/projects">View all</Link></Button>
        </header>
        {loading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-72 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {featured.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default Index;
