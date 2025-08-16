import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ChevronLeft, DollarSign, Tag, Layers, ShoppingCart, MessageCircle, ImageIcon, Eye } from "lucide-react";
import SEO from "@/components/SEO";
import { containerVariants, itemVariants, imageVariants } from "@/components/PageTransition";
import { api, endpoints } from "@/lib/api";
import { ServiceItem } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/EmptyState";
import LazyImage from "@/components/LazyImage";

// Animation variants now imported from PageTransition component

const priceVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5, delay: 0.2 },
  },
};

export default function ServiceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [service, setService] = useState<ServiceItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchService = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const { data } = await api.get<ServiceItem>(endpoints.serviceDetail(id));
        setService(data);
      } catch (e: any) {
        setError(e?.response?.status === 404 ? "Service not found" : "Failed to load service");
      } finally {
        setLoading(false);
      }
    };

    fetchService();
  }, [id]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const handleBuyNow = () => {
    if (!service) return;
    navigate('/contact', {
      state: {
        service: service.name,
        price: service.price,
        subject: `Service Inquiry: ${service.name}`,
        prefilledMessage: `Hi, I'm interested in the ${service.name} service (${formatPrice(service.price)}). Please provide more details about the process, timeline, and next steps.`
      }
    });
  };

  if (loading) {
    return (
      <div className="container py-10">
        <div className="mb-6">
          <Skeleton className="h-10 w-32 mb-4" />
          <Skeleton className="h-12 w-3/4 mb-2" />
          <Skeleton className="h-8 w-1/4" />
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

  if (error || !service) {
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
          title={error || "Service not found"}
          description="The service you're looking for doesn't exist or has been removed."
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
        title={`${service.name} | Studio Arc Services`}
        description={service.description.substring(0, 160)}
        canonical={`/services/${service.id}`}
      />

      <motion.div variants={itemVariants} className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate('/services')}
          className="mb-4 group hover:bg-primary/10 transition-colors"
        >
          <ChevronLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
          Back to Services
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
          <motion.div variants={priceVariants}>
            <Badge variant="default" className="flex items-center gap-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
              <DollarSign className="h-3 w-3" />
              {formatPrice(service.price)}
            </Badge>
          </motion.div>
        </div>

        <h1 className="font-heading text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
          {service.name}
        </h1>
      </motion.div>

      <div className="grid gap-8 lg:grid-cols-2">
        <motion.div variants={imageVariants} className="space-y-6">
          <Card className="overflow-hidden shadow-2xl group">
            <LazyImage
              src={service.icon || '/placeholder.svg'}
              alt={`${service.name} architectural service`}
              loading="eager"
              className="w-full h-auto object-cover aspect-square"
              enableLightbox={true}
              lightboxTitle={service.name}
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
            {service.album_images_count && service.album_images_count > 0 && (
              <div className="flex justify-center">
                <Button
                  onClick={() => navigate(`/services/${service.id}/album`)}
                  variant="outline"
                  size="lg"
                  className="group bg-background/50 backdrop-blur-sm border-primary/20 hover:bg-primary/10"
                >
                  <ImageIcon className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                  View Album ({service.album_images_count} {service.album_images_count === 1 ? 'Image' : 'Images'})
                  <Eye className="ml-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                </Button>
              </div>
            )}
            
            <div className="text-center text-sm text-muted-foreground">
              <p>Click image to view in full screen</p>
              {service.featured_album_images && service.featured_album_images.length > 0 && (
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
                Service Description
              </motion.h2>
              <motion.p 
                className="text-muted-foreground leading-relaxed"
                variants={itemVariants}
              >
                {service.description}
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
                Service Information
              </motion.h3>
              <motion.div className="space-y-3" variants={itemVariants}>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Service:</span>
                  <span className="font-medium">{service.name}</span>
                </div>
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Category:</span>
                  <span className="font-medium">{service.category_name || 'Not specified'}</span>
                </div>
                {service.subcategory_name && (
                  <>
                    <Separator />
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-muted-foreground">Subcategory:</span>
                      <span className="font-medium">{service.subcategory_name}</span>
                    </div>
                  </>
                )}
                <Separator />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-muted-foreground">Price:</span>
                  <motion.span 
                    className="text-2xl font-bold text-green-600 dark:text-green-400"
                    variants={priceVariants}
                  >
                    {formatPrice(service.price)}
                  </motion.span>
                </div>
              </motion.div>
            </CardContent>
          </Card>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-3">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="flex-1">
              <Button
                onClick={handleBuyNow}
                className="w-full"
                size="lg"
              >
                <ShoppingCart className="mr-2 h-4 w-4" />
                Get This Service
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                variant="outline"
                onClick={() => navigate('/contact', {
                  state: {
                    subject: `Question about ${service.name}`,
                    prefilledMessage: `Hi, I have some questions about the ${service.name} service. Could you provide more information?`
                  }
                })}
                className="w-full sm:w-auto"
                size="lg"
              >
                <MessageCircle className="mr-2 h-4 w-4" />
                Ask Questions
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      <motion.div
        variants={itemVariants}
        className="mt-12 grid gap-6 md:grid-cols-2"
      >
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold mb-3 text-blue-900 dark:text-blue-100">Why Choose This Service?</h3>
          <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
              Professional and experienced team
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
              Customized solutions for your needs
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
              Quality assurance and support
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
              Transparent pricing and timeline
            </li>
          </ul>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-green-200 dark:border-green-800">
          <h3 className="text-lg font-semibold mb-3 text-green-900 dark:text-green-100">Explore More Services</h3>
          <p className="text-sm text-green-800 dark:text-green-200 mb-4">
            Discover our full range of architectural and design services to bring your vision to life.
          </p>
          <Link to="/services">
            <Button variant="outline" className="group border-green-300 text-green-700 hover:bg-green-100 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-900/20">
              Browse All Services
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
        </Card>
      </motion.div>
    </motion.div>
  );
}
