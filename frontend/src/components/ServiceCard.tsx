import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ServiceItem } from "@/types";
import { useNavigate } from "react-router-dom";

interface Props {
  item: ServiceItem;
}

export default function ServiceCard({ item }: Props) {
  const navigate = useNavigate();

  const handleBuyNow = () => {
    navigate('/contact', { 
      state: { 
        service: item.name,
        price: item.price,
        prefilledMessage: `Hi, I'm interested in the ${item.name} service (${formatPrice(item.price)}). Please provide more details.`
      }
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  return (
    <Card className="overflow-hidden hover-scale">
      <CardHeader className="p-0">
        <img
          src={item.icon || '/placeholder.svg'}
          alt={`${item.name} architectural service`}
          loading="lazy"
          className="h-44 w-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder.svg';
          }}
        />
      </CardHeader>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium">{item.name}</h3>
          <span className="text-lg font-semibold text-primary">{formatPrice(item.price)}</span>
        </div>
        <p className="mt-1 mb-4 line-clamp-3 text-sm text-muted-foreground">{item.description}</p>
        <Button 
          onClick={handleBuyNow}
          className="w-full"
          size="sm"
        >
          Buy Now
        </Button>
      </CardContent>
    </Card>
  );
}
