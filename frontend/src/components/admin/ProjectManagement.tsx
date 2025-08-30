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
import { Plus, Edit, Trash2, Eye, ImageIcon, Upload, Tag, Layers, ChevronUp, ChevronDown, Search } from "lucide-react";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import UploadProgress from "@/components/UploadProgress";
import FileUpload from "@/components/FileUpload";
import { useUploadProgress } from "@/hooks/useUploadProgress";

const projectSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  project_date: z.string().min(1, "Project date is required"),
  order: z.coerce.number().min(1, "Order must be at least 1").optional(),
  categories: z.array(z.string()).optional(),
  subcategories: z.array(z.string()).optional(),
  image: z.any().optional(),
  album_images: z.any().optional(),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface Project {
  id: number;
  title: string;
  description: string;
  project_date: string;  // The manually entered project date
  order?: number;  // Manual ordering position
  categories?: number[];  // Array of category IDs
  subcategories?: number[];  // Array of subcategory IDs
  category_names?: string[];  // Array of category names from API
  subcategory_names?: string[];  // Array of subcategory names from API
  category_name?: string;  // First category name for display
  subcategory_name?: string;  // First subcategory name for display
  image?: string;
  original_filename?: string;  // Original filename when uploaded
  album_images_count?: number;
  featured_album_images?: any[];
}

interface ProjectManagementProps {
  onUpdate: () => void;
  onStorageUpdate?: () => void;
}

export default function ProjectManagement({ onUpdate, onStorageUpdate }: ProjectManagementProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [projectCategories, setProjectCategories] = useState<any[]>([]);
  const [subcategories, setSubcategories] = useState<any[]>([]);
  const [uploadMode, setUploadMode] = useState<'replace' | 'add'>('replace');
  
  const { uploadState, uploadFiles, pauseUpload, resumeUpload, cancelUpload, resetUpload } = useUploadProgress();

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      description: "",
      project_date: "",
      order: projects.length + 1,
      categories: [],
      subcategories: [],
    },
  });

  useEffect(() => {
    fetchProjects();
    fetchCategories();
    fetchAllSubcategories();
  }, []);

  // Filter projects based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredProjects(projects);
    } else {
      const filtered = projects.filter(project => 
        project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.category_names?.some(cat => cat.toLowerCase().includes(searchQuery.toLowerCase())) ||
        project.subcategory_names?.some(subcat => subcat.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredProjects(filtered);
    }
  }, [projects, searchQuery]);

  const fetchAllSubcategories = async () => {
    try {
      const response = await api.get(endpoints.admin.projectSubcategories);
      setSubcategories(response.data.results || response.data);
    } catch (error) {
      console.error("Error fetching subcategories:", error);
      toast({
        title: "Error",
        description: "Failed to load subcategories",
        variant: "destructive",
      });
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get(endpoints.admin.projectCategories);
      setProjectCategories(response.data.results || response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
      toast({
        title: "Error",
        description: "Failed to load categories",
        variant: "destructive",
      });
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await api.get(endpoints.admin.projects);
      const projectsData = response.data.results || response.data;
      setProjects(projectsData);
      setFilteredProjects(projectsData);
    } catch (error) {
      console.error("Error fetching projects:", error);
      toast({
        title: "Error",
        description: "Failed to load projects",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ProjectFormData) => {
    try {
      const formData = new FormData();
      formData.append("title", data.title);
      formData.append("description", data.description);
      formData.append("project_date", data.project_date);
      formData.append("order", data.order?.toString() || (projects.length + 1).toString());
      
      // Send category and subcategory IDs arrays
      if (data.categories && data.categories.length > 0) {
        data.categories.forEach(categoryId => {
          formData.append("categories", categoryId);
        });
      }
      
      if (data.subcategories && data.subcategories.length > 0) {
        data.subcategories.forEach(subcategoryId => {
          formData.append("subcategories", subcategoryId);
        });
      }
      
      // Always append image if provided (for both create and update)
      if (data.image && data.image[0]) {
        formData.append("image", data.image[0]);
      }

      let projectId = editingProject?.id;
      
      // Check if we have album images to upload
      const hasAlbumImages = data.album_images && data.album_images.length > 0;
      
      if (editingProject) {
        await api.patch(`${endpoints.admin.projects}${editingProject.id}/`, formData);
        if (!hasAlbumImages) {
          toast({ title: "Project updated successfully!" });
        }
      } else {
        const response = await api.post(endpoints.admin.projects, formData);
        projectId = response.data.id;
        if (!hasAlbumImages) {
          toast({ title: "Project created successfully!" });
        }
      }

      // Handle album images upload if provided
      if (hasAlbumImages && projectId) {
        // Close the dialog immediately and show progress bar
        setIsDialogOpen(false);
        
        const albumFiles = Array.from(data.album_images).map((file: File) => ({
          file,
          name: file.name,
          size: file.size
        }));

        console.log('Starting album upload for project:', projectId, 'with files:', albumFiles);

        const albumFormData = new FormData();
        albumFormData.append("project_id", projectId.toString());
        
        // Check upload mode
        if (uploadMode === 'replace') {
          // For replace mode, we need to delete existing images first
          // This will be handled by the backend when we send the replace flag
          albumFormData.append("replace_existing", "true");
        } else {
          // For add mode, we append to existing images
          albumFormData.append("replace_existing", "false");
        }

        try {
          await uploadFiles(
            albumFiles,
            endpoints.projectImagesBulkUpload,
            albumFormData,
            (response) => {
              console.log('Album upload success response:', response);
              const modeText = uploadMode === 'replace' ? 'replaced' : 'added to';
              toast({ 
                title: editingProject ? "Project updated successfully!" : "Project created successfully!",
                description: `${albumFiles.length} album images ${modeText} successfully!`
              });
              setEditingProject(null);
              form.reset();
              fetchProjects();
              onUpdate();
              onStorageUpdate?.(); // Update storage stats after file uploads
            },
            (error) => {
              console.error('Album upload error:', error);
              toast({
                title: "Album Upload Error",
                description: error,
                variant: "destructive",
              });
            }
          );
        } catch (uploadError) {
          console.error('Error in uploadFiles call:', uploadError);
          toast({
            title: "Upload Error",
            description: "Failed to start album upload process",
            variant: "destructive",
          });
        }
        
        // Exit early - upload progress will handle the rest
        return;
      }

      setIsDialogOpen(false);
      setEditingProject(null);
      form.reset();
      fetchProjects();
      onUpdate();
      // Update storage stats if an image was uploaded
      if (data.image && data.image[0]) {
        onStorageUpdate?.();
      }
    } catch (error: any) {
      console.error("Error saving project:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to save project",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    // Set upload mode based on whether project has existing images
    setUploadMode(project.featured_album_images && project.featured_album_images.length > 0 ? 'add' : 'replace');
    form.reset({
      title: project.title,
      description: project.description,
      project_date: project.project_date,
      order: project.order || projects.length + 1,
      categories: project.categories?.map(id => id.toString()) || [],
      subcategories: project.subcategories?.map(id => id.toString()) || [],
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this project?")) return;

    try {
      await api.delete(`${endpoints.admin.projects}${id}/`);
      toast({ title: "Project deleted successfully!" });
      fetchProjects();
      onUpdate();
      onStorageUpdate?.(); // Update storage stats after project deletion
    } catch (error) {
      console.error("Error deleting project:", error);
      toast({
        title: "Error",
        description: "Failed to delete project",
        variant: "destructive",
      });
    }
  };

  const handleNewProject = () => {
    setEditingProject(null);
    setUploadMode('replace'); // Default to replace mode for new projects
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    form.reset({
      title: "",
      description: "",
      project_date: today,
      order: projects.length + 1,
      categories: [],
      subcategories: [],
    });
    setIsDialogOpen(true);
  };

  const handleReorder = async (projectId: number, direction: 'up' | 'down') => {
    try {
      await api.post(`${endpoints.admin.projects}${projectId}/reorder/`, { direction });
      toast({ 
        title: `Project moved ${direction} successfully!`
      });
      fetchProjects();
      onUpdate();
    } catch (error: any) {
      console.error("Error reordering project:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || `Failed to move project ${direction}`,
        variant: "destructive",
      });
    }
  };

  const handleOrderChange = async (projectId: number, newOrder: number) => {
    if (newOrder < 1) {
      toast({
        title: "Error",
        description: "Order must be at least 1",
        variant: "destructive",
      });
      return;
    }

    try {
      await api.post(`${endpoints.admin.projects}${projectId}/reorder/`, { new_order: newOrder });
      toast({ 
        title: "Project order updated successfully!"
      });
      fetchProjects();
      onUpdate();
    } catch (error: any) {
      console.error("Error updating project order:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to update project order",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Project Management</CardTitle>
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
          <CardTitle>Project Management</CardTitle>
          <CardDescription>Manage your portfolio projects</CardDescription>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleNewProject}>
              <Plus className="h-4 w-4 mr-2" />
              Add Project
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[calc(100vw-2rem)] max-w-5xl h-[calc(100vh-2rem)] flex flex-col p-0">
            {/* Fixed Header */}
            <div className="flex-shrink-0 px-6 py-4 border-b">
              <DialogHeader>
                <DialogTitle className="text-xl">
                  {editingProject ? "Edit Project" : "Add New Project"}
                </DialogTitle>
                <DialogDescription className="text-base mt-2">
                  {editingProject 
                    ? "Update the project details below" 
                    : "Fill in the details to create a new project"
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
                          <label className="text-base font-medium">Title *</label>
                          <Input 
                            {...form.register("title")} 
                            placeholder="Enter project title"
                            className="h-12 text-base"
                          />
                          {form.formState.errors.title && (
                            <p className="text-sm text-destructive">
                              {form.formState.errors.title.message}
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <label className="text-base font-medium">Project Date *</label>
                          <Input 
                            type="date"
                            {...form.register("project_date")} 
                            className="h-12 text-base"
                          />
                          {form.formState.errors.project_date && (
                            <p className="text-sm text-destructive">
                              {form.formState.errors.project_date.message}
                            </p>
                          )}
                          <p className="text-sm text-muted-foreground">
                            When was this project completed?
                          </p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-base font-medium">Description *</label>
                        <Textarea 
                          {...form.register("description")} 
                          placeholder="Describe your project..."
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
                          min="0"
                          {...form.register("order")} 
                          placeholder="0"
                          className="w-32 h-12 text-base"
                        />
                        {form.formState.errors.order && (
                          <p className="text-sm text-destructive">
                            {form.formState.errors.order.message}
                          </p>
                        )}
                        <p className="text-sm text-muted-foreground">
                          Lower numbers appear first. Leave empty for automatic ordering.
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
                          {projectCategories.map((category) => (
                            <div key={category.id} className="flex items-center space-x-3 p-3 bg-card rounded-md border hover:border-primary/50 transition-all">
                              <Checkbox
                                id={`category-${category.id}`}
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
                              <label htmlFor={`category-${category.id}`} className="text-base cursor-pointer flex-1">
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
                                    id={`subcategory-${subcat.id}`}
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
                                  <label htmlFor={`subcategory-${subcat.id}`} className="text-base cursor-pointer flex-1">
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
                        <label className="text-base font-medium">Main Display Image</label>
                        {editingProject?.image && (
                          <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                            <p className="text-sm text-foreground mb-2">Current image:</p>
                            <p className="text-sm font-mono break-all text-muted-foreground">
                              {editingProject.original_filename?.replace(/\.[^/.]+$/, "") || 
                               editingProject.image.split('/').pop()?.replace(/\.[^/.]+$/, "") || 
                               'Unknown filename'}
                            </p>
                          </div>
                        )}
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <Input 
                            type="file" 
                            accept="image/*"
                            {...form.register("image")}
                            className="h-12 text-base"
                          />
                          <p className="text-sm text-muted-foreground mt-3">
                            Main project image for listings and detail page.
                            {editingProject?.image && " Leave empty to keep current image."}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="text-base font-medium flex items-center gap-2">
                          <ImageIcon className="h-5 w-5" />
                          Album Images
                        </label>
                        {editingProject?.featured_album_images && editingProject.featured_album_images.length > 0 && (
                          <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                            <p className="text-sm text-foreground mb-2">Current album ({editingProject.featured_album_images.length} images):</p>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {editingProject.featured_album_images.map((albumImage, index) => (
                                <p key={albumImage.id} className="text-xs font-mono break-all text-muted-foreground">
                                  {index + 1}. {albumImage.original_filename?.replace(/\.[^/.]+$/, "") || 
                                             albumImage.image.split('/').pop()?.replace(/\.[^/.]+$/, "") || 
                                             'Unknown filename'}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="space-y-4">
                          <div className="flex items-center space-x-4">
                            <label className="text-sm font-medium">Upload Mode:</label>
                            <div className="flex items-center space-x-2">
                              <input
                                type="radio"
                                id="upload-mode-replace"
                                name="uploadMode"
                                value="replace"
                                checked={uploadMode === 'replace'}
                                onChange={() => {
                                  setUploadMode('replace');
                                  // Reset album images when switching to replace mode
                                  if (editingProject?.featured_album_images && editingProject.featured_album_images.length > 0) {
                                    form.setValue("album_images", []);
                                  }
                                }}
                                className="h-4 w-4"
                              />
                              <label htmlFor="upload-mode-replace" className="text-sm cursor-pointer">
                                Replace all images
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input
                                type="radio"
                                id="upload-mode-add"
                                name="uploadMode"
                                value="add"
                                checked={uploadMode === 'add'}
                                onChange={() => setUploadMode('add')}
                                className="h-4 w-4"
                              />
                              <label htmlFor="upload-mode-add" className="text-sm cursor-pointer">
                                Add to existing album
                              </label>
                            </div>
                          </div>
                          
                          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                            <Input 
                              type="file" 
                              multiple
                              accept="image/*"
                              {...form.register("album_images")}
                              className="h-12 text-base"
                            />
                            <p className="text-sm text-muted-foreground mt-3">
                              {uploadMode === 'add' 
                                ? "Add new images to the existing album gallery."
                                : "Upload all images for the project album gallery."
                              }
                              {editingProject?.featured_album_images && editingProject.featured_album_images.length > 0 && 
                               uploadMode === 'add' &&
                               " New images will be appended to the current collection."
                              }
                            </p>
                          </div>
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
                    : editingProject 
                      ? "Update Project" 
                      : "Create Project"
                  }
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {/* Search Input */}
        <div className="mb-4">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          {searchQuery && (
            <p className="text-sm text-muted-foreground mt-2">
              Showing {filteredProjects.length} of {projects.length} projects
            </p>
          )}
        </div>
        <div className="rounded-md border">
          <div className="max-h-[800px] overflow-y-auto">
            <Table>
              <TableHeader className="sticky top-0 bg-background z-10">
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Subcategory</TableHead>
                  <TableHead>Album</TableHead>
                  <TableHead>Project Date</TableHead>
                  <TableHead>Order</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
              {filteredProjects.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    {searchQuery ? `No projects found matching "${searchQuery}"` : "No projects found. Create your first project to get started."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredProjects.map((project) => (
                  <TableRow 
                    key={project.id}
                    className="hover:bg-muted/50"
                  >
                    <TableCell className="font-medium">
                      {project.title}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {project.category_names && project.category_names.length > 0 ? (
                          project.category_names.map((categoryName, index) => (
                            <Badge key={index} variant="secondary">{categoryName}</Badge>
                          ))
                        ) : project.category_name ? (
                          <Badge variant="secondary">{project.category_name}</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {project.subcategory_names && project.subcategory_names.length > 0 ? (
                          project.subcategory_names.map((subcategoryName, index) => (
                            <Badge key={index} variant="outline">{subcategoryName}</Badge>
                          ))
                        ) : project.subcategory_name ? (
                          <Badge variant="outline">{project.subcategory_name}</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <ImageIcon className="h-4 w-4 text-muted-foreground" />
                        {project.album_images_count && project.album_images_count > 0 ? (
                          <>
                            <span className="text-sm">
                              {project.album_images_count} {(project.album_images_count === 1) ? 'image' : 'images'}
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(`/projects/${project.id}/album`, '_blank')}
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
                      {new Date(project.project_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          min="1"
                          value={project.order || 1}
                          onChange={(e) => {
                            const newOrder = parseInt(e.target.value);
                            if (!isNaN(newOrder) && newOrder !== project.order) {
                              handleOrderChange(project.id, newOrder);
                            }
                          }}
                          className="w-16 h-8 text-center text-sm font-mono"
                        />
                        <div className="flex flex-col gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleReorder(project.id, 'up')}
                            className="h-6 w-6 p-0"
                            disabled={project.order === 1}
                          >
                            <ChevronUp className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleReorder(project.id, 'down')}
                            className="h-6 w-6 p-0"
                            disabled={project.order === projects.length}
                          >
                            <ChevronDown className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end space-x-2">
                        {project.image && (
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => window.open(project.image, '_blank')}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleEdit(project)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDelete(project.id)}
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
          setEditingProject(null);
          form.reset();
          fetchProjects();
          onUpdate();
        }
      }}
      title={editingProject ? "Updating Project Album" : "Creating Project with Album"}
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