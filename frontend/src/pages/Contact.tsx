import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { MessageCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const schema = z.object({
  name: z.string().min(2, "Min 2 chars"),
  email: z.string().email(),
  message: z.string().min(10, "Min 10 chars"),
});

type Values = z.infer<typeof schema>;

interface LocationState {
  service?: string;
  price?: number;
  prefilledMessage?: string;
}

export default function ContactPage() {
  const location = useLocation();
  const state = location.state as LocationState;
  
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset, setValue } = useForm<Values>({ 
    resolver: zodResolver(schema) 
  });

  // Prefill message if coming from service page
  useEffect(() => {
    if (state?.prefilledMessage) {
      setValue('message', state.prefilledMessage);
    }
  }, [state, setValue]);

  const onSubmit = async (values: Values) => {
    try {
      // Add service information if available
      const payload = {
        ...values,
        service: state?.service || undefined
      };
      
      const response = await api.post(endpoints.contact, payload);
      
      if (response.data?.success) {
        toast({ 
          title: "Message sent successfully!", 
          description: response.data.message || "We'll get back to you soon."
        });
        reset();
        // Clear the service state after successful submission
        if (state?.service) {
          window.history.replaceState({}, '', '/contact');
        }
      } else {
        throw new Error(response.data?.message || "Failed to send message");
      }
    } catch (e: any) {
      console.error("Contact form error:", e);
      const errorMessage = e?.response?.data?.message || 
                          e?.response?.data?.errors?.non_field_errors?.[0] ||
                          e?.message || 
                          "Failed to send message. Please try again.";
      
      toast({ 
        title: "Failed to send message", 
        description: errorMessage,
        variant: "destructive"
      });
    }
  };

  const handleWhatsAppRedirect = () => {
    const phoneNumber = "+201026517446";
    
    // Get current form values
    const formValues = {
      name: (document.querySelector('input[name="name"]') as HTMLInputElement)?.value || '',
      email: (document.querySelector('input[name="email"]') as HTMLInputElement)?.value || '',
      message: (document.querySelector('textarea[name="message"]') as HTMLTextAreaElement)?.value || ''
    };

    // Create message based on service context or general inquiry
    let whatsappMessage = '';
    
    if (state?.service) {
      // Service inquiry message
      const price = state.price ? ` (${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(state.price)})` : '';
      
      // Check if the message already contains service information to avoid duplication
      const formattedPrice = state.price ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(state.price) : '';
      const isPrefilledMessage = formValues.message && 
        formValues.message.includes(state.service) && 
        (formattedPrice ? formValues.message.includes(formattedPrice) : true);
      
      if (isPrefilledMessage) {
        // Use the existing message as is since it already contains service info
        whatsappMessage = formValues.message;
      } else {
        // Create new service inquiry message
        whatsappMessage = `Hi! I'm interested in the ${state.service}${price} service.`;
        
        if (formValues.message && formValues.message.trim() !== '') {
          whatsappMessage += `\n\n${formValues.message}`;
        }
      }
      
      if (formValues.name && formValues.name.trim() !== '') {
        whatsappMessage += `\n\nName: ${formValues.name}`;
      }
      
      if (formValues.email && formValues.email.trim() !== '') {
        whatsappMessage += `\nEmail: ${formValues.email}`;
      }
    } else {
      // General inquiry message
      if (formValues.message && formValues.message.trim() !== '') {
        whatsappMessage = formValues.message;
      } else {
        whatsappMessage = 'Hi! I have an inquiry about your services.';
      }
      
      if (formValues.name && formValues.name.trim() !== '') {
        whatsappMessage += `\n\nName: ${formValues.name}`;
      }
      
      if (formValues.email && formValues.email.trim() !== '') {
        whatsappMessage += `\nEmail: ${formValues.email}`;
      }
    }

    // Encode the message for URL
    const encodedMessage = encodeURIComponent(whatsappMessage);
    const whatsappUrl = `https://wa.me/${phoneNumber.replace('+', '')}?text=${encodedMessage}`;
    
    // Open WhatsApp in a new window/tab
    window.open(whatsappUrl, '_blank');
  };

  return (
    <div className="container py-8 sm:py-10 px-4 sm:px-6 max-w-2xl">
      <SEO 
        title="Contact Alexandria Design | Architecture Studio in Egypt | Get Quote"
        description="Contact Alexandria Design for architectural services in Egypt. Get quotes for residential, commercial, and interior design projects. Professional architects in Alexandria, Egypt."
        canonical="/contact"
        keywords="contact Alexandria Design, architecture consultation Egypt, architectural services quote, Alexandria architects contact, Egypt architecture studio"
        structuredData={{
          "@context": "https://schema.org",
          "@type": "ContactPage",
          "mainEntity": {
            "@type": "Organization",
            "name": "Alexandria Design",
            "contactPoint": {
              "@type": "ContactPoint",
              "contactType": "Customer Service",
              "email": "mohamedaboelhamd765@gmail.com",
              "availableLanguage": ["English", "Arabic"]
            }
          }
        }}
      />
      <h1 className="font-heading text-2xl sm:text-3xl mb-4 sm:mb-6">Contact</h1>
      {state?.service && (
        <div className="mb-6 p-4 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground">Inquiring about:</p>
          <p className="font-medium">{state.service}</p>
          {state.price && (
            <p className="text-sm text-primary">
              {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(state.price)}
            </p>
          )}
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
        <div>
          <label className="mb-1 block text-sm">Name</label>
          <Input {...register("name")} />
          {errors.name && <p className="text-sm text-destructive mt-1">{errors.name.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <Input type="email" {...register("email")} />
          {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Message</label>
          <Textarea rows={6} {...register("message")} />
          {errors.message && <p className="text-sm text-destructive mt-1">{errors.message.message}</p>}
        </div>
        <div className="flex flex-col gap-3">
          <Button type="submit" disabled={isSubmitting} className="w-full" size="lg">
            {isSubmitting ? "Sending..." : "Send message"}
          </Button>
          <Button 
            type="button" 
            onClick={handleWhatsAppRedirect}
            className="w-full bg-green-600 hover:bg-green-700 text-white"
            size="lg"
          >
            <MessageCircle className="w-4 h-4 mr-2" />
            Send WhatsApp Message
          </Button>
        </div>
      </form>
    </div>
  );
}
