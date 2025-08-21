import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Edit, Trash2, Eye, ImageIcon, Upload, ChevronUp, ChevronDown, Tag, Layers } from "lucide-react";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import UploadProgress from "@/components/UploadProgress";
import FileUpload from "@/components/FileUpload";
import { useUploadProgress } from "@/hooks/useUploadProgress";

const serviceSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  price: z.number().min(0, "Price must be positive").optional(),
  order: z.coerce.number().min(1, "Order must be at least 1").optional(),
  categories: z.array(z.string()).optional(),
  subcategories: z.array(z.string()).optional(),
  icon: z.any().optional(),
  album_images: z.any().optional(),
});

type ServiceFormData = z.infer<typeof serviceSchema>;

interface Service {
  id: number;
  name: string;
  description: string;
  price?: number;
  order?: number;
  categories?: number[];
  subcategories?: number[];
  category_names?: string[];
  subcategory_names?: string[];
  category_name?: string;
  subcategory_name?: string;
  icon?: string;
  original_filename?: string;  // Original filename when uploaded
  album_images_count?: number;
  featured_album_images?: any[];
}

interface Category {
  id: number;
  name: string;
  description?: string;
}

interface Subcategory {
  id: number;
  name: string;
  description?: string;
  category: number;
  category_name: string;
}

interface ServiceManagementProps {
  onUpdate: () => void;
  onStorageUpdate?: () => void;
}

export default function ServiceManagement({ onUpdate, onStorageUpdate }: ServiceManagementProps) {
  const [services, setServices] = useState<Service[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  
  const { uploadState, uploadFiles, pauseUpload, resumeUpload, cancelUpload, resetUpload } = useUploadProgress();

  const form = useForm<ServiceFormData>({
    resolver: zodResolver(serviceSchema),
    defaultValues: {
      name: "",
      description: "",
      price: 0,
      order: 1,
      categories: [],
      subcategories: [],
    },
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [servicesRes, categoriesRes, subcategoriesRes] = await Promise.all([
        api.get(endpoints.admin.services),
        api.get(endpoints.admin.serviceCategories),
        api.get(endpoints.admin.serviceSubcategories),
      ]);

      setServices(servicesRes.data.results || servicesRes.data);
      setCategories(categoriesRes.data.results || categoriesRes.data);
      setSubcategories(subcategoriesRes.data.results || subcategoriesRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast({
        title: "Error",
        description: "Failed to load data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ServiceFormData) => {
    try {
      const formData = new FormData();
      formData.append("name", data.name);
      formData.append("description", data.description);
      if (data.price !== undefined) formData.append("price", data.price.toString());
      formData.append("order", data.order?.toString() || "0");
      
      // Append multiple categories
      if (data.categories) {
        data.categories.forEach(categoryId => {
          formData.append("categories", categoryId);
        });
      }
      
      // Append multiple subcategories
      if (data.subcategories) {
        data.subcategories.forEach(subcategoryId => {
          formData.append("subcategories", subcategoryId);
        });
      }
      
      if (data.icon && data.icon[0]) {
        formData.append("icon", data.icon[0]);
      }

      let serviceId = editingService?.id;
      
      // Check if we have album images to upload
      const hasAlbumImages = data.album_images && data.album_images.length > 0;
      
      if (editingService) {
        await api.patch(`${endpoints.admin.services}${editingService.id}/`, formData);
        if (!hasAlbumImages) {
          toast({ title: "Service updated successfully!" });
        }
      } else {
        const response = await api.post(endpoints.admin.services, formData);
        serviceId = response.data.id;
        if (!hasAlbumImages) {
          toast({ title: "Service created successfully!" });
        }
      }

      // Handle album images upload if provided
      if (hasAlbumImages && serviceId) {
        // Close the dialog immediately and show progress bar
        setIsDialogOpen(false);
        
        const albumFiles = Array.from(data.album_images).map((file: File) => ({
          file,
          name: file.name,
          size: file.size
        }));

        const albumFormData = new FormData();
        albumFormData.append("service_id", serviceId.toString());

        await uploadFiles(
          albumFiles,
          endpoints.serviceImagesBulkUpload,
          albumFormData,
          (response) => {
            toast({ 
              title: editingService ? "Service updated successfully!" : "Service created successfully!",
              description: `${albumFiles.length} album images uploaded successfully!`
            });
            setEditingService(null);
            form.reset();
            fetchData();
            onUpdate();
            onStorageUpdate?.(); // Update storage stats after file uploads
          },
          (error) => {
            toast({
              title: "Album Upload Error",
              description: error,
              variant: "destructive",
            });
          }
        );
        
        // Exit early - upload progress will handle the rest
        return;
      }

      setIsDialogOpen(false);
      setEditingService(null);
      form.reset();
      fetchData();
      onUpdate();
      // Update storage stats if an icon was uploaded
      if (data.icon && data.icon[0]) {
        onStorageUpdate?.();
      }
    } catch (error: any) {
      console.error("Error saving service:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to save service",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (service: Service) => {
    setEditingService(service);
    form.reset({
      name: service.name,
      description: service.description,
      price: service.price || 0,
      order: service.order || 1,
      categories: service.categories?.map(id => id.toString()) || [],
      subcategories: service.subcategories?.map(id => id.toString()) || [],
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this service?")) return;

    try {
      await api.delete(`${endpoints.admin.services}${id}/`);
      toast({ title: "Service deleted successfully!" });
      fetchData();
      onUpdate();
      onStorageUpdate?.(); // Update storage stats after service deletion
    } catch (error) {
      console.error("Error deleting service:", error);
      toast({
        title: "Error",
        description: "Failed to delete service",
        variant: "destructive",
      });
    }
  };

  const handleNewService = () => {
    setEditingService(null);
    // Set default order to next available position
    form.reset({
      name: "",
      description: "",
      price: 0,
      order: services.length + 1,
      categories: [],
      subcategories: [],
    });
    setIsDialogOpen(true);
  };

  const handleReorder = async (serviceId: number, direction: 'up' | 'down') => {
    try {
      await api.post(`${endpoints.admin.services}${serviceId}/reorder/`, { direction });
      toast({ 
        title: `Service moved ${direction} successfully!`
      });
      fetchData(); // Refresh the list to show new order
      onUpdate();
    } catch (error: any) {
      console.error("Error reordering service:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to reorder service",
        variant: "destructive",
      });
    }
  };

  const handleOrderChange = async (serviceId: number, newOrder: number) => {
    try {
      await api.post(`${endpoints.admin.services}${serviceId}/reorder/`, { new_order: newOrder });
      toast({ 
        title: "Service order updated successfully!"
      });
      fetchData(); // Refresh the list to show new order
      onUpdate();
    } catch (error: any) {
      console.error("Error updating service order:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to update service order",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Service Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Service Management</CardTitle>
          <CardDescription>Manage your services and offerings</CardDescription>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleNewService}>
              <Plus className="h-4 w-4 mr-2" />
              Add Service
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[calc(100vw-2rem)] max-w-5xl h-[calc(100vh-2rem)] flex flex-col p-0">
            {/* Fixed Header */}
            <div className="flex-shrink-0 px-6 py-4 border-b">
              <DialogHeader>
                <DialogTitle className="text-xl">
                  {editingService ? "Edit Service" : "Add New Service"}
                </DialogTitle>
                <DialogDescription className="text-base mt-2">
                  {editingService 
                    ? "Update the service details below" 
                    : "Fill in the details to create a new service"
                  }
                </DialogDescription>
              </DialogHeader>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="max-w-4xl mx-auto">
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                  {/* Basic Information */}
                  <div className="bg-card rounded-lg border p-6 space-y-6">
                    <h3 className="text-lg font-semibold">Basic Information</h3>
                    
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <label className="text-base font-medium">Service Name *</label>
                          <Input 
                            {...form.register("name")} 
                            placeholder="Enter service name"
                            className="h-12 text-base"
                          />
                          {form.formState.errors.name && (
                            <p className="text-sm text-destructive">
                              {form.formState.errors.name.message}
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <label className="text-base font-medium">Price (USD) *</label>
                          <Input 
                            type="number"
                            step="0.01"
                            min="0"
                            {...form.register("price", { valueAsNumber: true })} 
                            placeholder="0.00"
                            className="h-12 text-base"
                          />
                          {form.formState.errors.price && (
                            <p className="text-sm text-destructive">
                              {form.formState.errors.price.message}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-base font-medium">Description *</label>
                        <Textarea 
                          {...form.register("description")} 
                          placeholder="Describe your service..."
                          rows={4}
                          className="text-base resize-none"
                        />
                        {form.formState.errors.description && (
                          <p className="text-sm text-destructive">
                            {form.formState.errors.description.message}
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <label className="text-base font-medium">Display Order</label>
                        <Input 
                          type="number"
                          min="1"
                          {...form.register("order")} 
                          placeholder="1"
                          className="w-32 h-12 text-base"
                        />
                        {form.formState.errors.order && (
                          <p className="text-sm text-destructive">
                            {form.formState.errors.order.message}
                          </p>
                        )}
                        <p className="text-sm text-muted-foreground">
                          Lower numbers appear first. Services are ordered by this field, then by name.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Categories */}
                  <div className="bg-card rounded-lg border p-6 space-y-6">
                    <h3 className="text-lg font-semibold">Categories & Tags</h3>
                    
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <label className="text-base font-medium flex items-center gap-2">
                          <Tag className="h-5 w-5" />
                          Categories
                        </label>
                        <div className="space-y-3 max-h-64 overflow-y-auto border rounded-lg p-4 bg-muted/30">
                          {categories.map((category) => (
                            <div key={category.id} className="flex items-center space-x-3 p-3 bg-card rounded-md border hover:border-primary/50 transition-all">
                              <Checkbox
                                id={`service-category-${category.id}`}
                                checked={form.watch("categories")?.includes(category.id.toString()) || false}
                                onCheckedChange={(checked) => {
                                  const currentCategories = form.watch("categories") || [];
                                  if (checked) {
                                    form.setValue("categories", [...currentCategories, category.id.toString()]);
                                  } else {
                                    form.setValue("categories", currentCategories.filter(id => id !== category.id.toString()));
                                    const currentSubcategories = form.watch("subcategories") || [];
                                    const categorySubcategories = subcategories
                                      .filter(sub => sub.category === category.id)
                                      .map(sub => sub.id.toString());
                                    form.setValue("subcategories", 
                                      currentSubcategories.filter(id => !categorySubcategories.includes(id))
                                    );
                                  }
                                }}
                                className="h-5 w-5"
                              />
                              <label htmlFor={`service-category-${category.id}`} className="text-base cursor-pointer flex-1">
                                {category.name}
                              </label>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="text-base font-medium flex items-center gap-2">
                          <Layers className="h-5 w-5" />
                          Subcategories
                        </label>
                        <div className="space-y-3 max-h-64 overflow-y-auto border rounded-lg p-4 bg-muted/30">
                          {subcategories.length === 0 ? (
                            <div className="text-center py-8">
                              <p className="text-base text-muted-foreground">Loading...</p>
                            </div>
                          ) : subcategories.some(subcat => {
                            const selectedCategories = form.watch("categories") || [];
                            return selectedCategories.length === 0 || selectedCategories.includes(subcat.category.toString());
                          }) ? (
                            subcategories.map((subcat) => {
                              const selectedCategories = form.watch("categories") || [];
                              const shouldShow = selectedCategories.length === 0 || 
                                selectedCategories.includes(subcat.category.toString());
                              
                              if (!shouldShow) return null;
                              
                              return (
                                <div key={subcat.id} className="flex items-center space-x-3 p-3 bg-card rounded-md border hover:border-primary/50 transition-all">
                                  <Checkbox
                                    id={`service-subcategory-${subcat.id}`}
                                    checked={form.watch("subcategories")?.includes(subcat.id.toString()) || false}
                                    onCheckedChange={(checked) => {
                                      const currentSubcategories = form.watch("subcategories") || [];
                                      if (checked) {
                                        form.setValue("subcategories", [...currentSubcategories, subcat.id.toString()]);
                                      } else {
                                        form.setValue("subcategories", currentSubcategories.filter(id => id !== subcat.id.toString()));
                                      }
                                    }}
                                    className="h-5 w-5"
                                  />
                                  <label htmlFor={`service-subcategory-${subcat.id}`} className="text-base cursor-pointer flex-1">
                                    <div>{subcat.name}</div>
                                    <div className="text-sm text-muted-foreground">{subcat.category_name}</div>
                                  </label>
                                </div>
                              );
                            })
                          ) : (
                            <div className="text-center py-8">
                              <p className="text-base text-muted-foreground">
                                {form.watch("categories")?.length > 0 
                                  ? "No subcategories for selected categories" 
                                  : "Select categories to see subcategories"
                                }
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Images */}
                  <div className="bg-card rounded-lg border p-6 space-y-6">
                    <h3 className="text-lg font-semibold">Images</h3>
                    
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <label className="text-base font-medium">Service Icon</label>
                        {editingService?.icon && (
                          <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                            <p className="text-sm text-foreground mb-2">Current icon:</p>
                            <p className="text-sm font-mono break-all text-muted-foreground">
                              {editingService.original_filename?.replace(/\.[^/.]+$/, "") || 
                               editingService.icon.split('/').pop()?.replace(/\.[^/.]+$/, "") || 
                               'Unknown filename'}
                            </p>
                          </div>
                        )}
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <Input 
                            type="file" 
                            accept="image/*"
                            {...form.register("icon")}
                            className="h-12 text-base"
                          />
                          <p className="text-sm text-muted-foreground mt-3">
                            Service icon for listings and detail page.
                            {editingService?.icon && " Leave empty to keep current icon."}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="text-base font-medium flex items-center gap-2">
                          <ImageIcon className="h-5 w-5" />
                          Album Images
                        </label>
                        {editingService?.featured_album_images && editingService.featured_album_images.length > 0 && (
                          <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                            <p className="text-sm text-foreground mb-2">Current album ({editingService.featured_album_images.length} images):</p>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {editingService.featured_album_images.map((albumImage, index) => (
                                <p key={albumImage.id} className="text-xs font-mono break-all text-muted-foreground">
                                  {index + 1}. {albumImage.original_filename?.replace(/\.[^/.]+$/, "") || 
                                             albumImage.image.split('/').pop()?.replace(/\.[^/.]+$/, "") || 
                                             'Unknown filename'}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <Input 
                            type="file" 
                            multiple
                            accept="image/*"
                            {...form.register("album_images")}
                            className="h-12 text-base"
                          />
                          <p className="text-sm text-muted-foreground mt-3">
                            Multiple images for service album gallery.
                            {editingService?.featured_album_images && editingService.featured_album_images.length > 0 && " Leave empty to keep current, or add new images."}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            </div>

            {/* Fixed Footer */}
            <div className="flex-shrink-0 px-6 py-4 border-t bg-muted/30">
              <div className="flex justify-end space-x-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsDialogOpen(false)}
                  className="h-12 px-8 text-base"
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={form.formState.isSubmitting}
                  onClick={form.handleSubmit(onSubmit)}
                  className="h-12 px-8 text-base"
                >
                  {form.formState.isSubmitting 
                    ? "Saving..." 
                    : editingService 
                      ? "Update Service" 
                      : "Create Service"
                  }
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Subcategory</TableHead>
                <TableHead>Album</TableHead>
                <TableHead>Order</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {services.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    No services found. Create your first service to get started.
                  </TableCell>
                </TableRow>
              ) : (
                services.map((service) => (
                  <TableRow key={service.id}>
                    <TableCell className="font-medium">{service.name}</TableCell>
                    <TableCell>
                      {service.price !== undefined ? (
                        <span className="font-semibold text-green-600">
                          ${new Intl.NumberFormat('en-US', { 
                            minimumFractionDigits: 2, 
                            maximumFractionDigits: 2 
                          }).format(service.price)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">Not set</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {service.category_names && service.category_names.length > 0 ? (
                          service.category_names.map((categoryName, index) => (
                            <Badge key={index} variant="secondary">{categoryName}</Badge>
                          ))
                        ) : service.category_name ? (
                          <Badge variant="secondary">{service.category_name}</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {service.subcategory_names && service.subcategory_names.length > 0 ? (
                          service.subcategory_names.map((subcategoryName, index) => (
                            <Badge key={index} variant="outline">{subcategoryName}</Badge>
                          ))
                        ) : service.subcategory_name ? (
                          <Badge variant="outline">{service.subcategory_name}</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <ImageIcon className="h-4 w-4 text-muted-foreground" />
                        {service.album_images_count && service.album_images_count > 0 ? (
                          <>
                            <span className="text-sm">
                              {service.album_images_count} {(service.album_images_count === 1) ? 'image' : 'images'}
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(`/services/${service.id}/album`, '_blank')}
                              className="h-6 px-2 text-xs"
                            >
                              View
                            </Button>
                          </>
                        ) : (
                          <span className="text-sm text-muted-foreground">No album</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          min="1"
                          value={service.order || 1}
                          onChange={(e) => {
                            const newOrder = parseInt(e.target.value);
                            if (!isNaN(newOrder) && newOrder !== service.order) {
                              handleOrderChange(service.id, newOrder);
                            }
                          }}
                          className="w-16 h-8 text-center text-sm font-mono"
                        />
                        <div className="flex flex-col gap-0">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => handleReorder(service.id, 'up')}
                            title="Move up"
                          >
                            <ChevronUp className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => handleReorder(service.id, 'down')}
                            title="Move down"
                          >
                            <ChevronDown className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end space-x-2">
                        {service.icon && (
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => window.open(service.icon, '_blank')}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleEdit(service)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDelete(service.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    {/* Upload Progress Modal */}
    <UploadProgress
      isOpen={uploadState.isUploading || uploadState.isCompleted}
      onClose={() => {
        resetUpload();
        if (uploadState.isCompleted && !uploadState.error) {
          setIsDialogOpen(false);
          setEditingService(null);
          form.reset();
          fetchData();
          onUpdate();
        }
      }}
      title={editingService ? "Updating Service Album" : "Creating Service with Album"}
      totalFiles={uploadState.totalFiles}
      uploadedFiles={uploadState.uploadedFiles}
      currentFileName={uploadState.currentFileName}
      currentFileProgress={uploadState.currentFileProgress}
      overallProgress={uploadState.overallProgress}
      uploadSpeed={uploadState.uploadSpeed}
      estimatedTimeRemaining={uploadState.estimatedTimeRemaining}
      totalBytes={uploadState.totalBytes}
      uploadedBytes={uploadState.uploadedBytes}
      remainingBytes={uploadState.remainingBytes}
      error={uploadState.error}
      isCompleted={uploadState.isCompleted}
      isPaused={uploadState.isPaused}
      onPause={pauseUpload}
      onResume={resumeUpload}
      onCancel={cancelUpload}
    />
    </>
  );
}
