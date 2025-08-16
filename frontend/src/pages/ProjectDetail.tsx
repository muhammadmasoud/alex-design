import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ChevronLeft, Calendar, Tag, Layers, ImageIcon, Eye } from "lucide-react";
import SEO from "@/components/SEO";
import { containerVariants, itemVariants, imageVariants } from "@/components/PageTransition";
import { api, endpoints } from "@/lib/api";
import { Project } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/EmptyState";
import LazyImage from "@/components/LazyImage";

// Animation variants now imported from PageTransition component

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProject = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const { data } = await api.get<Project>(endpoints.projectDetail(id));
        setProject(data);
      } catch (e: any) {
        setError(e?.response?.status === 404 ? "Project not found" : "Failed to load project");
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [id]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="container py-10">
        <div className="mb-6">
          <Skeleton className="h-10 w-32 mb-4" />
          <Skeleton className="h-12 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <div className="grid gap-8 lg:grid-cols-2">
          <Skeleton className="h-96 w-full rounded-lg" />
          <div className="space-y-6">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container py-10">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/projects')}
            className="mb-4"
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Button>
        </div>
        <EmptyState
          title={error || "Project not found"}
          description="The project you're looking for doesn't exist or has been removed."
        />
      </div>
    );
  }

  return (
    <motion.div
      className="container py-10"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <SEO
        title={`${project.title} | Studio Arc`}
        description={project.description.substring(0, 160)}
        canonical={`/projects/${project.id}`}
      />

      <motion.div variants={itemVariants} className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate('/projects')}
          className="mb-4 group hover:bg-primary/10 transition-colors"
        >
          <ChevronLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
          Back to Projects
        </Button>
        
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {project.category_name && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Tag className="h-3 w-3" />
              {project.category_name}
            </Badge>
          )}
          {project.subcategory_name && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              {project.subcategory_name}
            </Badge>
          )}
          <Badge variant="outline" className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(project.created_at)}
          </Badge>
        </div>

        <h1 className="font-heading text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
          {project.title}
        </h1>
      </motion.div>

      <div className="grid gap-8 lg:grid-cols-2">
        <motion.div variants={imageVariants} className="space-y-6">
          <Card className="overflow-hidden shadow-2xl group">
            <LazyImage
              src={project.image || '/placeholder.svg'}
              alt={`${project.title} architecture project`}
              loading="eager"
              className="w-full h-auto object-cover"
              enableLightbox={true}
              lightboxTitle={project.title}
              showZoomIcon={true}
            />
          </Card>
          
          {/* Album button and Image info */}
          <motion.div 
            className="space-y-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {project.album_images_count > 0 && (
              <div className="flex justify-center">
                <Button
                  onClick={() => navigate(`/projects/${project.id}/album`)}
                  variant="outline"
                  size="lg"
                  className="group bg-background/50 backdrop-blur-sm border-primary/20 hover:bg-primary/10"
                >
                  <ImageIcon className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                  View Album ({project.album_images_count} {project.album_images_count === 1 ? 'Image' : 'Images'})
                  <Eye className="ml-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                </Button>
              </div>
            )}
            
            <div className="text-center text-sm text-muted-foreground">
              <p>Click image to view in full screen</p>
              {project.featured_album_images && project.featured_album_images.length > 0 && (
                <p className="mt-1">Browse additional images in the album</p>
              )}
            </div>
          </motion.div>
        </motion.div>

        <motion.div variants={itemVariants} className="space-y-6">
          <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardContent className="p-6">
              <motion.h2 
                className="text-2xl font-semibold mb-4 flex items-center gap-2"
                variants={itemVariants}
              >
                <motion.div
                  className="w-1 h-6 bg-primary rounded-full"
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                />
                Project Overview
              </motion.h2>
              <motion.p 
                className="text-muted-foreground leading-relaxed"
                variants={itemVariants}
              >
                {project.description}
              </motion.p>
            </CardContent>
          </Card>

          <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardContent className="p-6">
              <motion.h3 
                className="text-xl font-semibold mb-4 flex items-center gap-2"
                variants={itemVariants}
              >
                <motion.div
                  className="w-1 h-5 bg-secondary rounded-full"
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                />
                Project Details
              </motion.h3>
              <motion.div className="space-y-3" variants={itemVariants}>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Project:</span>
                  <span className="font-medium">{project.title}</span>
                </div>
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Category:</span>
                  <span className="font-medium">{project.category_name || 'Not specified'}</span>
                </div>
                {project.subcategory_name && (
                  <>
                    <Separator />
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-muted-foreground">Subcategory:</span>
                      <span className="font-medium">{project.subcategory_name}</span>
                    </div>
                  </>
                )}
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Created:</span>
                  <span className="font-medium">{formatDate(project.created_at)}</span>
                </div>
              </motion.div>
            </CardContent>
          </Card>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-3">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={() => navigate('/contact', {
                  state: {
                    subject: `Inquiry about ${project.title}`,
                    prefilledMessage: `Hi, I'm interested in learning more about the "${project.title}" project. Could you provide additional details?`
                  }
                })}
                className="w-full sm:w-auto"
                size="lg"
              >
                Get More Info
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                variant="outline"
                onClick={() => navigate('/services')}
                className="w-full sm:w-auto"
                size="lg"
              >
                View Our Services
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      <motion.div
        variants={itemVariants}
        className="mt-12 p-6 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-lg border"
      >
        <h3 className="text-lg font-semibold mb-3">Interested in Similar Projects?</h3>
        <p className="text-muted-foreground mb-4">
          Explore more of our architectural portfolio to see other innovative designs and solutions.
        </p>
        <Link to="/projects">
          <Button variant="outline" className="group">
            Browse All Projects
            <motion.span
              className="ml-2"
              initial={{ x: 0 }}
              whileHover={{ x: 5 }}
              transition={{ duration: 0.2 }}
            >
              →
            </motion.span>
          </Button>
        </Link>
      </motion.div>
    </motion.div>
  );
}
