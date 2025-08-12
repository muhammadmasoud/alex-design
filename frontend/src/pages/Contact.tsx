import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLocation } from "react-router-dom";
import { useEffect } from "react";
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

  return (
    <div className="container py-10 max-w-2xl">
      <SEO title="Contact | Studio Arc" description="Get in touch with our architecture studio." canonical="/contact" />
      <h1 className="font-heading text-3xl mb-6">Contact</h1>
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
        <Button type="submit" disabled={isSubmitting} className="w-full sm:w-auto">{isSubmitting ? "Sending..." : "Send message"}</Button>
      </form>
    </div>
  );
}
