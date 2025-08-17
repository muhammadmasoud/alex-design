import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ServiceItem } from "@/types";
import { useNavigate } from "react-router-dom";
import { ShoppingCart, Eye, DollarSign, Tag } from "lucide-react";
import { motion } from "framer-motion";
import OptimizedImage from "@/components/OptimizedImage";

interface Props {
  item: ServiceItem;
}

export default function ServiceCard({ item }: Props) {
  const navigate = useNavigate();

  const handleBuyNow = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    navigate('/contact', { 
      state: { 
        service: item.name,
        price: item.price,
        subject: `Service Inquiry: ${item.name}`,
        prefilledMessage: `Hi, I'm interested in the ${item.name} service (${formatPrice(item.price)}). Please provide more details.`
      }
    });
  };

  const handleViewDetails = () => {
    navigate(`/services/${item.id}`);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card 
        className="overflow-hidden cursor-pointer group shadow-lg hover:shadow-xl transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm"
        onClick={handleViewDetails}
      >
        <CardHeader className="p-0 relative">
          <div className="relative overflow-hidden h-44">
            <OptimizedImage
              src={item.icon || '/placeholder.svg'}
              alt={`${item.name} architectural service`}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              effect="blur"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = '/placeholder.svg';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="bg-white/90 dark:bg-black/90 rounded-full p-2 backdrop-blur-sm">
                <Eye className="h-4 w-4 text-gray-700 dark:text-gray-300" />
              </div>
            </div>
          </div>
          <div className="absolute top-3 left-3 flex flex-col gap-2">
            {item.category_name && (
              <Badge variant="secondary" className="bg-white/90 dark:bg-black/90 text-gray-700 dark:text-gray-300 backdrop-blur-sm">
                <Tag className="h-3 w-3 mr-1" />
                {item.category_name}
              </Badge>
            )}
            <Badge variant="default" className="bg-green-100/90 dark:bg-green-900/90 text-green-800 dark:text-green-100 backdrop-blur-sm">
              <DollarSign className="h-3 w-3 mr-1" />
              {formatPrice(item.price)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-3 sm:p-4">
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <h3 className="font-semibold text-base sm:text-lg leading-tight group-hover:text-primary transition-colors duration-200">
                {item.name}
              </h3>
            </div>
            <p className="line-clamp-2 text-xs sm:text-sm text-muted-foreground leading-relaxed">
              {item.description}
            </p>
            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <Button 
                onClick={handleBuyNow}
                className="flex-1 w-full sm:w-auto"
                size="sm"
              >
                <ShoppingCart className="h-4 w-4 mr-1" />
                Buy Now
              </Button>
              <div className="text-xs text-primary font-medium text-center sm:self-center group-hover:underline">
                View Details →
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
