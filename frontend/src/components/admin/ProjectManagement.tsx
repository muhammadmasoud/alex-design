import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Edit, Trash2, Eye, ImageIcon, Upload } from "lucide-react";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import UploadProgress from "@/components/UploadProgress";
import FileUpload from "@/components/FileUpload";
import { useUploadProgress } from "@/hooks/useUploadProgress";

const projectSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  category: z.string().optional(),
  subcategory: z.string().optional(),
  image: z.any().optional(),
  album_images: z.any().optional(),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface Project {
  id: number;
  title: string;
  description: string;
  category?: number;  // Now a foreign key ID
  subcategory?: number;  // Now a foreign key ID
  category_name?: string;
  subcategory_name?: string;
  category_obj?: { id: number; name: string };
  subcategory_obj?: { id: number; name: string };
  image?: string;
  album_images_count?: number;
  featured_album_images?: any[];
  created_at: string;
}

interface ProjectManagementProps {
  onUpdate: () => void;
  onStorageUpdate?: () => void;
}

export default function ProjectManagement({ onUpdate, onStorageUpdate }: ProjectManagementProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [projectCategories, setProjectCategories] = useState<any[]>([]);
  
  const { uploadState, uploadFiles, pauseUpload, resumeUpload, cancelUpload, resetUpload } = useUploadProgress();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [subcategories, setSubcategories] = useState<any[]>([]);

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      description: "",
      category: "",
      subcategory: "",
    },
  });

  useEffect(() => {
    fetchProjects();
    fetchCategories();
  }, []);

  useEffect(() => {
    if (selectedCategoryId) {
      fetchSubcategories(selectedCategoryId);
    } else {
      setSubcategories([]);
    }
  }, [selectedCategoryId]);

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

  const fetchSubcategories = async (categoryId: number) => {
    try {
      const response = await api.get(endpoints.admin.projectSubcategories, {
        params: { category: categoryId }
      });
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

  const fetchProjects = async () => {
    try {
      const response = await api.get(endpoints.projects);
      setProjects(response.data.results || response.data);
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
      
      // Send category and subcategory IDs instead of names
      if (selectedCategoryId) {
        formData.append("category", selectedCategoryId.toString());
      }
      
      // Find subcategory ID by name
      if (data.subcategory) {
        const selectedSubcategory = subcategories.find(sub => sub.name === data.subcategory);
        if (selectedSubcategory) {
          formData.append("subcategory", selectedSubcategory.id.toString());
        }
      }
      
      // Always append image if provided (for both create and update)
      if (data.image && data.image[0]) {
        formData.append("image", data.image[0]);
      }

      let projectId = editingProject?.id;
      
      // Check if we have album images to upload
      const hasAlbumImages = data.album_images && data.album_images.length > 0;
      
      if (editingProject) {
        await api.patch(`${endpoints.projects}${editingProject.id}/`, formData);
        if (!hasAlbumImages) {
          toast({ title: "Project updated successfully!" });
        }
      } else {
        const response = await api.post(endpoints.projects, formData);
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

        const albumFormData = new FormData();
        albumFormData.append("project_id", projectId.toString());

        await uploadFiles(
          albumFiles,
          endpoints.projectImagesBulkUpload,
          albumFormData,
          (response) => {
            toast({ 
              title: editingProject ? "Project updated successfully!" : "Project created successfully!",
              description: `${albumFiles.length} album images uploaded successfully!`
            });
            setEditingProject(null);
            form.reset();
            fetchProjects();
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
    // Use the category ID from the project
    setSelectedCategoryId(typeof project.category === 'number' ? project.category : null);
    form.reset({
      title: project.title,
      description: project.description,
      category: project.category?.toString() || "",
      subcategory: project.subcategory_name || "",
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this project?")) return;

    try {
      await api.delete(`${endpoints.projects}${id}/`);
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
    setSelectedCategoryId(null);
    form.reset();
    setIsDialogOpen(true);
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
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>
                {editingProject ? "Edit Project" : "Add New Project"}
              </DialogTitle>
              <DialogDescription>
                {editingProject 
                  ? "Update the project details below" 
                  : "Fill in the details to create a new project"
                }
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Title</label>
                <Input 
                  {...form.register("title")} 
                  placeholder="Enter project title"
                />
                {form.formState.errors.title && (
                  <p className="text-sm text-destructive mt-1">
                    {form.formState.errors.title.message}
                  </p>
                )}
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Description</label>
                <Textarea 
                  {...form.register("description")} 
                  placeholder="Enter project description"
                  rows={3}
                />
                {form.formState.errors.description && (
                  <p className="text-sm text-destructive mt-1">
                    {form.formState.errors.description.message}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Category</label>
                  <Select 
                    value={selectedCategoryId?.toString() || ""} 
                    onValueChange={(value) => {
                      const categoryId = value ? parseInt(value) : null;
                      setSelectedCategoryId(categoryId);
                      // Clear subcategory when category changes
                      form.setValue("subcategory", "");
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {projectCategories.map((category) => (
                        <SelectItem key={category.id} value={category.id.toString()}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Subcategory</label>
                  <Select 
                    value={form.watch("subcategory")} 
                    onValueChange={(value) => form.setValue("subcategory", value)}
                    disabled={!selectedCategoryId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={selectedCategoryId ? "Select subcategory" : "Select category first"} />
                    </SelectTrigger>
                    <SelectContent>
                      {subcategories.map((subcat) => (
                        <SelectItem key={subcat.id} value={subcat.name}>
                          {subcat.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Main Display Image</label>
                <Input 
                  type="file" 
                  accept="image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.tiff,.tif,.heic,.heif"
                  {...form.register("image")}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  This image will be shown in project listings and as the main image on the detail page.
                </p>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 flex items-center gap-2">
                  <ImageIcon className="h-4 w-4" />
                  Project Album Images
                </label>
                <Input 
                  type="file" 
                  multiple
                  accept="image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.tiff,.tif,.heic,.heif"
                  {...form.register("album_images")}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Select multiple images for the project album. Visitors can view all these images by clicking "View Album" on the project detail page.
                </p>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={form.formState.isSubmitting}>
                  {form.formState.isSubmitting 
                    ? "Saving..." 
                    : editingProject 
                      ? "Update Project" 
                      : "Create Project"
                  }
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Subcategory</TableHead>
                <TableHead>Album</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    No projects found. Create your first project to get started.
                  </TableCell>
                </TableRow>
              ) : (
                projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">{project.title}</TableCell>
                    <TableCell>
                      {project.category_name && (
                        <Badge variant="secondary">{project.category_name}</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {project.subcategory_name && (
                        <Badge variant="outline">{project.subcategory_name}</Badge>
                      )}
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
                      {new Date(project.created_at).toLocaleDateString()}
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
