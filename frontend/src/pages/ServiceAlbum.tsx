import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ChevronLeft, Tag, Layers, ImageIcon, DollarSign, Expand } from "lucide-react";
import SEO from "@/components/SEO";
import { containerVariants, itemVariants } from "@/components/PageTransition";
import { api, endpoints } from "@/lib/api";
import { ServiceAlbumResponse, AlbumImage } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/EmptyState";
import ImageLightbox from "@/components/ImageLightbox";
import ProgressiveImage from "@/components/ProgressiveImage";
import { cn } from "@/lib/utils";

const albumGridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const albumItemVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
  },
};

export default function ServiceAlbum() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [albumData, setAlbumData] = useState<ServiceAlbumResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [currentImage, setCurrentImage] = useState<AlbumImage | null>(null);

  useEffect(() => {
    const fetchAlbum = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const { data } = await api.get<ServiceAlbumResponse>(endpoints.serviceAlbum(id));
        setAlbumData(data);
      } catch (e: any) {
        setError(e?.response?.status === 404 ? "Service or album not found" : "Failed to load album");
      } finally {
        setLoading(false);
      }
    };

    fetchAlbum();
  }, [id]);

  const handleImageClick = (image: AlbumImage, index: number) => {
    // Ensure we have a valid image URL before opening lightbox
    if (!image.image || image.image.includes('placeholder')) {
      console.warn('Cannot open lightbox: invalid image URL', image.image);
      return;
    }
    
    setCurrentImage(image);
    setCurrentImageIndex(index);
    setLightboxOpen(true);
  };

  const handleImageError = (image: AlbumImage) => {
    console.warn('Image failed to load:', image.image);
    // You could implement additional error handling here
  };

  if (loading) {
    return (
      <div className="container py-10">
        <div className="mb-6">
          <Skeleton className="h-10 w-32 mb-4" />
          <Skeleton className="h-12 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !albumData) {
    return (
      <div className="container py-10">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/services')}
            className="mb-4"
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Services
          </Button>
        </div>
        <EmptyState
          title={error || "Album not found"}
          description="The service album you're looking for doesn't exist or has been removed."
        />
      </div>
    );
  }

  const { service, album_images, total_images } = albumData;

  if (total_images === 0) {
    return (
      <motion.div
        className="container py-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <SEO
          title={`${service.name} Album | Studio Arc`}
          description={`View all images from the ${service.name} service`}
          canonical={`/services/${service.id}/album`}
        />

        <motion.div variants={itemVariants} className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate(`/services/${service.id}`)}
            className="mb-4 group hover:bg-primary/10 transition-colors"
          >
            <ChevronLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            Back to Service
          </Button>
          
          <h1 className="font-heading text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            {service.name} Album
          </h1>
        </motion.div>

        <EmptyState
          title="No Album Images"
          description="This service doesn't have any album images yet."
        />
      </motion.div>
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
        title={`${service.name} Album | Studio Arc`}
        description={`View all ${total_images} images from the ${service.name} service`}
        canonical={`/services/${service.id}/album`}
      />

      <motion.div variants={itemVariants} className="mb-8">
        <Button
          variant="ghost"
          onClick={() => navigate(`/services/${service.id}`)}
          className="mb-4 group hover:bg-primary/10 transition-colors"
        >
          <ChevronLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
          Back to Service
        </Button>
        
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {service.category_name && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Tag className="h-3 w-3" />
              {service.category_name}
            </Badge>
          )}
          {service.subcategory_name && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              {service.subcategory_name}
            </Badge>
          )}
          {service.price && (
            <Badge variant="outline" className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" />
              {service.price}
            </Badge>
          )}
          <Badge variant="outline" className="flex items-center gap-1">
            <ImageIcon className="h-3 w-3" />
            {total_images} {total_images === 1 ? 'Image' : 'Images'}
          </Badge>
        </div>

        <h1 className="font-heading text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
          {service.name} Album
        </h1>
        
        {service.description && (
          <p className="text-muted-foreground text-lg max-w-3xl">
            {service.description}
          </p>
        )}
      </motion.div>

      <motion.div
        className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
        variants={albumGridVariants}
        initial="hidden"
        animate="visible"
      >
        {album_images.map((image: AlbumImage, index: number) => (
          <motion.div
            key={image.id}
            variants={albumItemVariants}
            className="group"
          >
            <Card className="overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 group-hover:scale-[1.02]">
              <div 
                className="relative cursor-pointer group"
                onClick={() => handleImageClick(image, index)}
              >
                <ProgressiveImage
                  src={image.image}
                  alt={image.title || `${service.name} - Image ${index + 1}`}
                  className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-105"
                  priority={false}
                  onError={() => handleImageError(image)}
                />

                {image.title && (
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                    <h3 className="text-white font-medium text-sm truncate">
                      {image.title}
                    </h3>
                  </div>
                )}
              </div>
              {image.description && (
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {image.description}
                  </p>
                </CardContent>
              )}
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Navigation Footer */}
      <motion.div
        variants={itemVariants}
        className="mt-12 p-6 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-lg border"
      >
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold mb-1">Interested in This Service?</h3>
            <p className="text-muted-foreground">
              Get in touch to learn more about our services and how we can help you.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={() => navigate('/contact', {
                state: {
                  subject: `Inquiry about ${service.name}`,
                  prefilledMessage: `Hi, I'm interested in learning more about the "${service.name}" service. Could you provide additional details?`
                }
              })}
            >
              Get More Info
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/services')}
            >
              Browse All Services
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Centralized Lightbox */}
      {currentImage && (
        <ImageLightbox
          isOpen={lightboxOpen}
          onClose={() => setLightboxOpen(false)}
          src={currentImage.image}
          alt={currentImage.title || `${service.name} - Image ${currentImageIndex + 1}`}
          title={currentImage.title || `${service.name} - Image ${currentImageIndex + 1}`}
        />
      )}
    </motion.div>
  );
}
