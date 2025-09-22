import { useState, useEffect, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Edit, Trash2, Eye, ImageIcon, Tag, Layers, ChevronUp, ChevronDown, Search, Building2, Palette } from "lucide-react";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import UploadProgress from "@/components/UploadProgress";
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
  project_date: string;
  order?: number;
  categories?: number[];
  subcategories?: number[];
  category_names?: string[];
  subcategory_names?: string[];
  category_name?: string;
  subcategory_name?: string;
  image?: string;
  original_filename?: string;
  album_images_count?: number;
  featured_album_images?: any[];
}

interface ProjectManagementWithTabsProps {
  onUpdate: () => void;
  onStorageUpdate?: () => void;
}

export default function ProjectManagementWithTabs({ onUpdate, onStorageUpdate }: ProjectManagementWithTabsProps) {
  // State for both project categories
  const [architectureProjects, setArchitectureProjects] = useState<Project[]>([]);
  const [interiorProjects, setInteriorProjects] = useState<Project[]>([]);
  const [filteredArchitectureProjects, setFilteredArchitectureProjects] = useState<Project[]>([]);
  const [filteredInteriorProjects, setFilteredInteriorProjects] = useState<Project[]>([]);
  
  // Search states for each tab
  const [architectureSearchQuery, setArchitectureSearchQuery] = useState("");
  const [interiorSearchQuery, setInteriorSearchQuery] = useState("");
  
  // Common state
  const [loading, setLoading] = useState(true);
  const [reorderingProjectId, setReorderingProjectId] = useState<number | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [projectCategories, setProjectCategories] = useState<any[]>([]);
  const [subcategories, setSubcategories] = useState<any[]>([]);
  const [uploadMode, setUploadMode] = useState<'replace' | 'add'>('replace');
  const [activeTab, setActiveTab] = useState<'architecture' | 'interior'>('architecture');
  const [currentCategory, setCurrentCategory] = useState<'Architecture Design' | 'Interior Design'>('Architecture Design');
  
  // Refs for scroll position preservation
  const architectureScrollRef = useRef<HTMLDivElement>(null);
  const interiorScrollRef = useRef<HTMLDivElement>(null);
  
  const { uploadState, uploadFiles, pauseUpload, resumeUpload, cancelUpload, resetUpload } = useUploadProgress();

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      description: "",
      project_date: "",
      order: 1,
      categories: [],
      subcategories: [],
    },
  });

  useEffect(() => {
    fetchProjects();
    fetchCategories();
    fetchAllSubcategories();
  }, []);

  // Filter architecture projects based on search query
  useEffect(() => {
    if (!architectureSearchQuery.trim()) {
      setFilteredArchitectureProjects(architectureProjects);
    } else {
      const filtered = architectureProjects.filter(project => 
        project.title.toLowerCase().includes(architectureSearchQuery.toLowerCase()) ||
        project.description.toLowerCase().includes(architectureSearchQuery.toLowerCase()) ||
        project.category_names?.some(cat => cat.toLowerCase().includes(architectureSearchQuery.toLowerCase())) ||
        project.subcategory_names?.some(subcat => subcat.toLowerCase().includes(architectureSearchQuery.toLowerCase()))
      );
      setFilteredArchitectureProjects(filtered);
    }
  }, [architectureProjects, architectureSearchQuery]);

  // Filter interior projects based on search query
  useEffect(() => {
    if (!interiorSearchQuery.trim()) {
      setFilteredInteriorProjects(interiorProjects);
    } else {
      const filtered = interiorProjects.filter(project => 
        project.title.toLowerCase().includes(interiorSearchQuery.toLowerCase()) ||
        project.description.toLowerCase().includes(interiorSearchQuery.toLowerCase()) ||
        project.category_names?.some(cat => cat.toLowerCase().includes(interiorSearchQuery.toLowerCase())) ||
        project.subcategory_names?.some(subcat => subcat.toLowerCase().includes(interiorSearchQuery.toLowerCase()))
      );
      setFilteredInteriorProjects(filtered);
    }
  }, [interiorProjects, interiorSearchQuery]);

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

  // Helper function to preserve scroll position
  const preserveScrollPosition = (callback: () => Promise<void>) => {
    return async () => {
      // Save current scroll positions
      const archScrollTop = architectureScrollRef.current?.scrollTop || 0;
      const interiorScrollTop = interiorScrollRef.current?.scrollTop || 0;
      
      // Execute the callback
      await callback();
      
      // Restore scroll positions after a small delay to ensure DOM has updated
      setTimeout(() => {
        if (architectureScrollRef.current) {
          architectureScrollRef.current.scrollTop = archScrollTop;
        }
        if (interiorScrollRef.current) {
          interiorScrollRef.current.scrollTop = interiorScrollTop;
        }
      }, 50);
    };
  };

  const fetchProjects = async () => {
    try {
      setLoading(true);
      
      // Fetch Architecture Design projects
      const architectureResponse = await api.get(endpoints.admin.projects, {
        params: { category: 'Architecture Design' }
      });
      const architectureData = architectureResponse.data.results || architectureResponse.data;
      setArchitectureProjects(architectureData);
      setFilteredArchitectureProjects(architectureData);

      // Fetch Interior Design projects
      const interiorResponse = await api.get(endpoints.admin.projects, {
        params: { category: 'Interior Design' }
      });
      const interiorData = interiorResponse.data.results || interiorResponse.data;
      setInteriorProjects(interiorData);
      setFilteredInteriorProjects(interiorData);

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
      // CLIENT-SIDE VALIDATION FOR LARGE UPLOADS
      const albumFiles = data.album_images ? Array.from(data.album_images as FileList) : [];
      const mainImageFile = data.image?.[0] as File | undefined;
      
      // Validate individual file sizes (50MB limit per file)
      const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
      const oversizedFiles: string[] = [];
      
      if (mainImageFile && mainImageFile.size > MAX_FILE_SIZE) {
        oversizedFiles.push(`${mainImageFile.name} (${(mainImageFile.size / 1024 / 1024).toFixed(1)}MB)`);
      }
      
      albumFiles.forEach((file) => {
        const fileObj = file as File;
        if (fileObj.size > MAX_FILE_SIZE) {
          oversizedFiles.push(`${fileObj.name} (${(fileObj.size / 1024 / 1024).toFixed(1)}MB)`);
        }
      });
      
      if (oversizedFiles.length > 0) {
        toast({
          title: "Files Too Large",
          description: `The following files exceed the 50MB limit: ${oversizedFiles.join(', ')}`,
          variant: "destructive",
        });
        return;
      }
      
      // Validate total upload size (warn if over 500MB)
      const totalSize = (mainImageFile?.size || 0) + albumFiles.reduce((sum: number, file) => {
        const fileObj = file as File;
        return sum + fileObj.size;
      }, 0);
      const WARN_SIZE_THRESHOLD = 500 * 1024 * 1024; // 500MB
      
      if (totalSize > WARN_SIZE_THRESHOLD) {
        const confirmed = window.confirm(
          `This upload is ${(totalSize / 1024 / 1024).toFixed(0)}MB total. Large uploads may take several minutes. Continue?`
        );
        if (!confirmed) return;
      }

      const formData = new FormData();
      formData.append("title", data.title);
      formData.append("description", data.description);
      formData.append("project_date", data.project_date);
      
      // Get the current projects count for the active category to set proper order
      const currentProjects = activeTab === 'architecture' ? architectureProjects : interiorProjects;
      formData.append("order", data.order?.toString() || (currentProjects.length + 1).toString());
      
      // Always include the current category based on active tab
      const categoryId = projectCategories.find(cat => 
        cat.name === currentCategory
      )?.id;
      
      if (categoryId) {
        formData.append("categories", categoryId.toString());
      }
      
      // Add other categories if selected
      if (data.categories && data.categories.length > 0) {
        data.categories.forEach(categoryIdStr => {
          // Avoid duplicate category IDs
          if (categoryIdStr !== categoryId?.toString()) {
            formData.append("categories", categoryIdStr);
          }
        });
      }
      
      if (data.subcategories && data.subcategories.length > 0) {
        data.subcategories.forEach(subcategoryId => {
          formData.append("subcategories", subcategoryId);
        });
      }
      
      // Check if we have main image to upload
      const hasMainImage = data.image && data.image[0];
      const hasAlbumImages = data.album_images && data.album_images.length > 0;
      
      // CASE 1: Text-only update (no images)
      if (!hasMainImage && !hasAlbumImages) {
        if (editingProject) {
          await api.patch(`${endpoints.admin.projects}${editingProject.id}/`, formData);
          toast({ title: "Project updated successfully!" });
        } else {
          await api.post(endpoints.admin.projects, formData);
          toast({ title: "Project created successfully!" });
        }
        setIsDialogOpen(false);
        setEditingProject(null);
        form.reset();
        fetchProjects();
        onUpdate();
        return;
      }

      // CASE 2: Has images - use upload progress system
      let projectId = editingProject?.id;
      
      // Always append image if provided (for both create and update)  
      if (hasMainImage) {
        formData.append("image", data.image[0]);
      }
      
      // If updating existing project with main image only, use upload progress
      if (editingProject && hasMainImage && !hasAlbumImages) {
        // Close dialog immediately and show progress
        setIsDialogOpen(false);
        
        const mainImageFile = data.image[0] as File;
        const uploadFile = {
          file: mainImageFile,
          name: mainImageFile.name,
          size: mainImageFile.size
        };
        
        try {
          await uploadFiles(
            [uploadFile],
            `${endpoints.admin.projects}${editingProject.id}/`,
            formData,
            () => {
              toast({ 
                title: "Project updated successfully!", 
                description: "Main image is being optimized in the background." 
              });
              setEditingProject(null);
              form.reset();
              fetchProjects();
              onUpdate();
              onStorageUpdate?.();
            },
            (error) => {
              toast({
                title: "Main Image Upload Error",
                description: error,
                variant: "destructive",
              });
            },
            'PATCH',
            'image'
          );
        } catch (uploadError) {
          console.error('Error in main image upload:', uploadError);
          toast({
            title: "Upload Error",
            description: "Failed to upload main image. Please try again.",
            variant: "destructive",
          });
        }
        return;
      }
      
      // For new projects or projects with album images, handle accordingly
      if (editingProject) {
        // Update existing project first
        await api.patch(`${endpoints.admin.projects}${editingProject.id}/`, formData);
        projectId = editingProject.id;
        
        if (!hasAlbumImages) {
          const hasMainImageUpdate = data.image && data.image[0];
          if (hasMainImageUpdate) {
            toast({ 
              title: "Project updated successfully!", 
              description: "Main image is being optimized in the background." 
            });
          } else {
            toast({ title: "Project updated successfully!" });
          }
          setIsDialogOpen(false);
          setEditingProject(null);
          form.reset();
          fetchProjects();
          onUpdate();
          return;
        }
      } else {
        // Create new project with main image - use progress if has main image
        if (hasMainImage && !hasAlbumImages) {
          // Close dialog immediately and show progress for new project with main image
          setIsDialogOpen(false);
          
          const mainImageFile = data.image[0] as File;
          const uploadFile = {
            file: mainImageFile,
            name: mainImageFile.name,
            size: mainImageFile.size
          };
          
          try {
            await uploadFiles(
              [uploadFile],
              endpoints.admin.projects,
              formData,
              () => {
                toast({ 
                  title: "Project created successfully!", 
                  description: "Main image is being optimized in the background." 
                });
                setEditingProject(null);
                form.reset();
                fetchProjects();
                onUpdate();
                onStorageUpdate?.();
              },
              (error) => {
                toast({
                  title: "Project Creation Error",
                  description: error,
                  variant: "destructive",
                });
              },
              'POST',
              'image'
            );
          } catch (uploadError) {
            console.error('Error in project creation upload:', uploadError);
            toast({
              title: "Upload Error",
              description: "Failed to create project with image. Please try again.",
              variant: "destructive",
            });
          }
          return;
        } else {
          // Create new project without main image or with album images
          const response = await api.post(endpoints.admin.projects, formData);
          projectId = response.data.id;
          if (!hasAlbumImages) {
            toast({ title: "Project created successfully!" });
            setIsDialogOpen(false);
            setEditingProject(null);
            form.reset();
            fetchProjects();
            onUpdate();
            return;
          }
        }
      }

      // Handle album images upload if provided
      if (hasAlbumImages && projectId) {
        // Close the dialog immediately and show progress bar
        setIsDialogOpen(false);
        
        const albumFiles = Array.from(data.album_images as FileList).map((file) => ({
          file: file as File,
          name: (file as File).name,
          size: (file as File).size
        }));

        const albumFormData = new FormData();
        albumFormData.append("project_id", projectId.toString());
        
        if (uploadMode === 'replace') {
          albumFormData.append("replace_existing", "true");
        } else {
          albumFormData.append("replace_existing", "false");
        }

        try {
          await uploadFiles(
            albumFiles,
            endpoints.projectImagesBulkUpload,
            albumFormData,
            () => {
              const modeText = uploadMode === 'replace' ? 'replaced' : 'added to';
              toast({ 
                title: editingProject ? "Project updated successfully!" : "Project created successfully!",
                description: `${albumFiles.length} album images ${modeText} successfully!`
              });
              setEditingProject(null);
              form.reset();
              fetchProjects();
              onUpdate();
              onStorageUpdate?.();
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
        
        return;
      }

      setIsDialogOpen(false);
      setEditingProject(null);
      form.reset();
      fetchProjects();
      onUpdate();
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
    
    // Determine which tab this project belongs to based on its categories
    const isArchitecture = project.category_names?.includes('Architecture Design');
    const isInterior = project.category_names?.includes('Interior Design');
    
    if (isArchitecture) {
      setActiveTab('architecture');
      setCurrentCategory('Architecture Design');
    } else if (isInterior) {
      setActiveTab('interior');
      setCurrentCategory('Interior Design');
    }

    form.reset({
      title: project.title,
      description: project.description,
      project_date: project.project_date,
      order: project.order || 1,
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
      await preserveScrollPosition(fetchProjects)();
      onUpdate();
      onStorageUpdate?.();
    } catch (error) {
      console.error("Error deleting project:", error);
      toast({
        title: "Error",
        description: "Failed to delete project",
        variant: "destructive",
      });
    }
  };

  const handleNewProject = (category: 'Architecture Design' | 'Interior Design') => {
    setEditingProject(null);
    setUploadMode('replace');
    setCurrentCategory(category);
    
    // Switch to the appropriate tab
    setActiveTab(category === 'Architecture Design' ? 'architecture' : 'interior');
    
    // Get current projects count for the selected category
    const currentProjects = category === 'Architecture Design' ? architectureProjects : interiorProjects;
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    
    // Auto-select the appropriate category
    const categoryId = projectCategories.find(cat => cat.name === category)?.id;
    
    form.reset({
      title: "",
      description: "",
      project_date: today,
      order: currentProjects.length + 1,
      categories: categoryId ? [categoryId.toString()] : [],
      subcategories: [],
    });
    setIsDialogOpen(true);
  };

  const handleReorder = async (projectId: number, direction: 'up' | 'down') => {
    try {
      // Set loading state for visual feedback
      setReorderingProjectId(projectId);
      
      // Show immediate feedback
      toast({ 
        title: `Moving project ${direction}...`,
        description: "Updating all project positions..."
      });
      
      await api.post(`${endpoints.admin.projects}${projectId}/reorder/`, { direction });
      
      // Immediately refresh the project lists to show updated positions while preserving scroll
      await preserveScrollPosition(fetchProjects)();
      onUpdate();
      
      toast({ 
        title: `Project moved ${direction} successfully!`,
        description: "All project positions have been updated."
      });
    } catch (error: any) {
      console.error("Error reordering project:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || `Failed to move project ${direction}`,
        variant: "destructive",
      });
    } finally {
      setReorderingProjectId(null);
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
      // Set loading state for visual feedback
      setReorderingProjectId(projectId);
      
      // Show immediate feedback
      toast({ 
        title: "Updating project position...",
        description: `Moving to position ${newOrder} and updating all other positions...`
      });
      
      await api.post(`${endpoints.admin.projects}${projectId}/reorder/`, { new_order: newOrder });
      
      // Immediately refresh the project lists to show updated positions while preserving scroll
      await preserveScrollPosition(fetchProjects)();
      onUpdate();
      
      toast({ 
        title: "Project order updated successfully!",
        description: `Project moved to position ${newOrder}. All positions have been updated.`
      });
    } catch (error: any) {
      console.error("Error updating project order:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to update project order",
        variant: "destructive",
      });
    } finally {
      setReorderingProjectId(null);
    }
  };

  const renderProjectTable = (projects: Project[], searchQuery: string, setSearchQuery: (query: string) => void, categoryName: string, scrollRef: React.RefObject<HTMLDivElement>) => {
    return (
      <>
        {/* Search Input */}
        <div className="mb-4">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder={`Search ${categoryName.toLowerCase()} projects...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          {searchQuery && (
            <p className="text-sm text-muted-foreground mt-2">
              Showing {projects.length} results
            </p>
          )}
        </div>
        
        <div className="rounded-md border">
          {reorderingProjectId && (
            <div className="bg-blue-50 border-b border-blue-200 px-4 py-2 text-sm text-blue-700 flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              Updating project positions...
            </div>
          )}
          <div ref={scrollRef} className="max-h-[600px] overflow-y-auto">
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
                {projects.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      {searchQuery ? `No ${categoryName.toLowerCase()} projects found matching "${searchQuery}"` : `No ${categoryName.toLowerCase()} projects found. Create your first project to get started.`}
                    </TableCell>
                  </TableRow>
                ) : (
                  projects.map((project) => (
                    <TableRow 
                      key={project.id}
                      className={`hover:bg-muted/50 ${
                        reorderingProjectId === project.id ? 'bg-blue-50 border-blue-200' : 
                        reorderingProjectId ? 'opacity-75' : ''
                      }`}
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
                            defaultValue={project.order || 1}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                const newOrder = parseInt(e.currentTarget.value);
                                if (!isNaN(newOrder) && newOrder !== project.order && newOrder >= 1) {
                                  handleOrderChange(project.id, newOrder);
                                } else if (isNaN(newOrder) || newOrder < 1) {
                                  // Reset to original value if invalid
                                  e.currentTarget.value = (project.order || 1).toString();
                                }
                                e.currentTarget.blur(); // Remove focus after Enter
                              }
                            }}
                            onBlur={(e) => {
                              const newOrder = parseInt(e.target.value);
                              if (!isNaN(newOrder) && newOrder !== project.order && newOrder >= 1) {
                                handleOrderChange(project.id, newOrder);
                              } else if (isNaN(newOrder) || newOrder < 1) {
                                // Reset to original value if invalid
                                e.target.value = (project.order || 1).toString();
                              }
                            }}
                            className={`w-16 h-8 text-center text-sm font-mono ${
                              reorderingProjectId === project.id ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                            title="Type new order number and press Enter or click outside"
                            disabled={reorderingProjectId === project.id}
                          />
                          <div className="flex flex-col gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleReorder(project.id, 'up')}
                              className="h-6 w-6 p-0"
                              disabled={project.order === 1 || reorderingProjectId === project.id}
                            >
                              {reorderingProjectId === project.id ? (
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current"></div>
                              ) : (
                                <ChevronUp className="h-3 w-3" />
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleReorder(project.id, 'down')}
                              className="h-6 w-6 p-0"
                              disabled={project.order === projects.length || reorderingProjectId === project.id}
                            >
                              {reorderingProjectId === project.id ? (
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current"></div>
                              ) : (
                                <ChevronDown className="h-3 w-3" />
                              )}
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
      </>
    );
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
        <CardHeader>
          <div>
            <CardTitle>Project Management</CardTitle>
            <CardDescription>Manage your portfolio projects by category</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'architecture' | 'interior')}>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <TabsList className="grid w-full max-w-md grid-cols-2">
                <TabsTrigger value="architecture" className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Architecture Design ({architectureProjects.length})
                </TabsTrigger>
                <TabsTrigger value="interior" className="flex items-center gap-2">
                  <Palette className="h-4 w-4" />
                  Interior Design ({interiorProjects.length})
                </TabsTrigger>
              </TabsList>
              
              <div className="flex gap-2">
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => handleNewProject('Architecture Design')} variant="outline">
                      <Plus className="h-4 w-4 mr-2" />
                      <Building2 className="h-4 w-4 mr-1" />
                      Architecture
                    </Button>
                  </DialogTrigger>
                </Dialog>
                
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => handleNewProject('Interior Design')}>
                      <Plus className="h-4 w-4 mr-2" />
                      <Palette className="h-4 w-4 mr-1" />
                      Interior
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="w-[calc(100vw-2rem)] max-w-5xl h-[calc(100vh-2rem)] flex flex-col p-0">
                    {/* Dialog content would go here - same as original component */}
                    {/* For brevity, I'll reference the original dialog structure */}
                    {/* Fixed Header */}
                    <div className="flex-shrink-0 px-6 py-4 border-b">
                      <DialogHeader>
                        <DialogTitle className="text-xl">
                          {editingProject ? "Edit Project" : `Add New ${currentCategory} Project`}
                        </DialogTitle>
                        <DialogDescription className="text-base mt-2">
                          {editingProject 
                            ? "Update the project details below" 
                            : `Fill in the details to create a new ${currentCategory.toLowerCase()} project`
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
                                  Lower numbers appear first within the {currentCategory.toLowerCase()} category.
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* Categories */}
                          <div className="bg-card rounded-lg border p-6 space-y-6">
                            <h3 className="text-lg font-semibold">Categories & Tags</h3>
                            
                            <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                              <p className="text-sm text-primary font-medium">
                                📋 Primary Category: {currentCategory}
                              </p>
                              <p className="text-xs text-muted-foreground mt-1">
                                This project will be automatically categorized under "{currentCategory}". 
                                You can add additional categories below if needed.
                              </p>
                            </div>
                            
                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                              <div className="space-y-4">
                                <label className="text-base font-medium flex items-center gap-2">
                                  <Tag className="h-5 w-5" />
                                  Additional Categories
                                </label>
                                <div className="space-y-3 max-h-64 overflow-y-auto border rounded-lg p-4 bg-muted/30">
                                  {projectCategories.map((category) => {
                                    // Skip the primary category as it's already selected
                                    if (category.name === currentCategory) return null;
                                    
                                    return (
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
                                    );
                                  })}
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
                                    // Show subcategories for the primary category or selected additional categories
                                    const primaryCategoryId = projectCategories.find(cat => cat.name === currentCategory)?.id;
                                    const selectedCategories = form.watch("categories") || [];
                                    const allSelectedCategories = primaryCategoryId ? [primaryCategoryId.toString(), ...selectedCategories] : selectedCategories;
                                    return allSelectedCategories.length === 0 || allSelectedCategories.includes(subcat.category.toString());
                                  }) ? (
                                    subcategories.map((subcat) => {
                                      const primaryCategoryId = projectCategories.find(cat => cat.name === currentCategory)?.id;
                                      const selectedCategories = form.watch("categories") || [];
                                      const allSelectedCategories = primaryCategoryId ? [primaryCategoryId.toString(), ...selectedCategories] : selectedCategories;
                                      const shouldShow = allSelectedCategories.length === 0 || 
                                        allSelectedCategories.includes(subcat.category.toString());
                                      
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
                                        No subcategories available for selected categories
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
              </div>
            </div>

            <TabsContent value="architecture">
              {renderProjectTable(filteredArchitectureProjects, architectureSearchQuery, setArchitectureSearchQuery, "Architecture Design", architectureScrollRef)}
            </TabsContent>

            <TabsContent value="interior">
              {renderProjectTable(filteredInteriorProjects, interiorSearchQuery, setInteriorSearchQuery, "Interior Design", interiorScrollRef)}
            </TabsContent>
          </Tabs>
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
        title={editingProject ? "Updating Project Album" : `Creating ${currentCategory} Project with Album`}
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
        error={uploadState.error || undefined}
        isCompleted={uploadState.isCompleted}
        isPaused={uploadState.isPaused}
        onPause={pauseUpload}
        onResume={resumeUpload}
        onCancel={cancelUpload}
      />
    </>
  );
}
