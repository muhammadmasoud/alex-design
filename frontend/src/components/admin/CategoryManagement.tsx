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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Edit, Trash2, FolderOpen, Tag } from "lucide-react";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const categorySchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
});

const subcategorySchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  category: z.number(),
});

type CategoryFormData = z.infer<typeof categorySchema>;
type SubcategoryFormData = z.infer<typeof subcategorySchema>;

interface Category {
  id: number;
  name: string;
  description?: string;
  subcategories_count: number;
  subcategories_names: string[];
  created_at: string;
}

interface Subcategory {
  id: number;
  name: string;
  description?: string;
  category: number;
  category_name: string;
  created_at: string;
}

interface CategoryManagementProps {
  onUpdate: () => void;
}

export default function CategoryManagement({ onUpdate }: CategoryManagementProps) {
  const [projectCategories, setProjectCategories] = useState<Category[]>([]);
  const [serviceCategories, setServiceCategories] = useState<Category[]>([]);
  const [projectSubcategories, setProjectSubcategories] = useState<Subcategory[]>([]);
  const [serviceSubcategories, setServiceSubcategories] = useState<Subcategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [subcategoryDialogOpen, setSubcategoryDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [editingSubcategory, setEditingSubcategory] = useState<Subcategory | null>(null);
  const [currentCategoryType, setCurrentCategoryType] = useState<'project' | 'service'>('project');

  const categoryForm = useForm<CategoryFormData>({
    resolver: zodResolver(categorySchema),
    defaultValues: { name: "", description: "" },
  });

  const subcategoryForm = useForm<SubcategoryFormData>({
    resolver: zodResolver(subcategorySchema),
    defaultValues: { name: "", description: "", category: 0 },
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      setLoading(true);
      
      const [projectCats, serviceCats, projectSubs, serviceSubs] = await Promise.all([
        api.get(endpoints.admin.projectCategories),
        api.get(endpoints.admin.serviceCategories),
        api.get(endpoints.admin.projectSubcategories),
        api.get(endpoints.admin.serviceSubcategories),
      ]);

      // Handle both paginated and non-paginated responses
      const projectCategoriesData = projectCats.data.results || projectCats.data || [];
      const serviceCategoriesData = serviceCats.data.results || serviceCats.data || [];
      const projectSubcategoriesData = projectSubs.data.results || projectSubs.data || [];
      const serviceSubcategoriesData = serviceSubs.data.results || serviceSubs.data || [];

      console.log("Fetched data:", {
        projectCategories: projectCategoriesData.length,
        serviceCategories: serviceCategoriesData.length,
        projectSubcategories: projectSubcategoriesData.length,
        serviceSubcategories: serviceSubcategoriesData.length,
      });

      setProjectCategories(projectCategoriesData);
      setServiceCategories(serviceCategoriesData);
      setProjectSubcategories(projectSubcategoriesData);
      setServiceSubcategories(serviceSubcategoriesData);
    } catch (error: any) {
      console.error("Error fetching categories:", error);
      setError("Failed to load categories. Please try again.");
      toast({
        title: "Error",
        description: "Failed to load categories",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySubmit = async (data: CategoryFormData) => {
    try {
      const endpoint = currentCategoryType === 'project' 
        ? endpoints.admin.projectCategories 
        : endpoints.admin.serviceCategories;

      if (editingCategory) {
        await api.patch(`${endpoint}${editingCategory.id}/`, data);
        toast({ title: "Category updated successfully!" });
      } else {
        await api.post(endpoint, data);
        toast({ title: "Category created successfully!" });
      }

      setCategoryDialogOpen(false);
      setEditingCategory(null);
      categoryForm.reset();
      fetchData();
      onUpdate();
    } catch (error: any) {
      console.error("Error saving category:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to save category",
        variant: "destructive",
      });
    }
  };

  const handleSubcategorySubmit = async (data: SubcategoryFormData) => {
    try {
      // Validate that a category is selected
      if (!data.category || data.category === 0) {
        subcategoryForm.setError("category", { 
          type: "manual", 
          message: "Please select a category" 
        });
        return;
      }

      const endpoint = currentCategoryType === 'project' 
        ? endpoints.admin.projectSubcategories 
        : endpoints.admin.serviceSubcategories;

      if (editingSubcategory) {
        await api.patch(`${endpoint}${editingSubcategory.id}/`, data);
        toast({ title: "Subcategory updated successfully!" });
      } else {
        await api.post(endpoint, data);
        toast({ title: "Subcategory created successfully!" });
      }

      setSubcategoryDialogOpen(false);
      setEditingSubcategory(null);
      subcategoryForm.reset();
      fetchData();
      onUpdate();
    } catch (error: any) {
      console.error("Error saving subcategory:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to save subcategory",
        variant: "destructive",
      });
    }
  };

  const handleDeleteCategory = async (id: number, type: 'project' | 'service') => {
    if (!confirm("Are you sure you want to delete this category? This will also delete all its subcategories.")) return;

    try {
      const endpoint = type === 'project' 
        ? endpoints.admin.projectCategories 
        : endpoints.admin.serviceCategories;
      
      await api.delete(`${endpoint}${id}/`);
      toast({ title: "Category deleted successfully!" });
      fetchData();
      onUpdate();
    } catch (error: any) {
      console.error("Error deleting category:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to delete category",
        variant: "destructive",
      });
    }
  };

  const handleDeleteSubcategory = async (id: number, type: 'project' | 'service') => {
    if (!confirm("Are you sure you want to delete this subcategory?")) return;

    try {
      const endpoint = type === 'project' 
        ? endpoints.admin.projectSubcategories 
        : endpoints.admin.serviceSubcategories;
      
      await api.delete(`${endpoint}${id}/`);
      toast({ title: "Subcategory deleted successfully!" });
      fetchData();
      onUpdate();
    } catch (error: any) {
      console.error("Error deleting subcategory:", error);
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to delete subcategory",
        variant: "destructive",
      });
    }
  };

  const openCategoryDialog = (type: 'project' | 'service', category?: Category) => {
    setCurrentCategoryType(type);
    setEditingCategory(category || null);
    categoryForm.reset(category ? { name: category.name, description: category.description } : { name: "", description: "" });
    setCategoryDialogOpen(true);
  };

  const openSubcategoryDialog = (type: 'project' | 'service', subcategory?: Subcategory) => {
    setCurrentCategoryType(type);
    setEditingSubcategory(subcategory || null);
    subcategoryForm.reset(subcategory ? {
      name: subcategory.name,
      description: subcategory.description,
      category: subcategory.category
    } : { name: "", description: "", category: 0 });
    setSubcategoryDialogOpen(true);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Category Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-2">Loading categories...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Category Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={fetchData}>Try Again</Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Database Summary Dashboard */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Project Categories</CardTitle>
              <FolderOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{projectCategories.length}</div>
              <p className="text-xs text-muted-foreground">Active categories</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Project Subcategories</CardTitle>
              <Tag className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{projectSubcategories.length}</div>
              <p className="text-xs text-muted-foreground">Active subcategories</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Service Categories</CardTitle>
              <FolderOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{serviceCategories.length}</div>
              <p className="text-xs text-muted-foreground">Active categories</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Service Subcategories</CardTitle>
              <Tag className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{serviceSubcategories.length}</div>
              <p className="text-xs text-muted-foreground">Active subcategories</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
      <CardHeader>
        <CardTitle>Category Management</CardTitle>
        <CardDescription>Manage project and service categories and subcategories</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="project-categories" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="project-categories">Project Categories</TabsTrigger>
            <TabsTrigger value="project-subcategories">Project Subcategories</TabsTrigger>
            <TabsTrigger value="service-categories">Service Categories</TabsTrigger>
            <TabsTrigger value="service-subcategories">Service Subcategories</TabsTrigger>
          </TabsList>

          {/* Project Categories */}
          <TabsContent value="project-categories" className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Project Categories</h3>
                <p className="text-sm text-muted-foreground">Total: {projectCategories.length} categories</p>
              </div>
              <Button onClick={() => openCategoryDialog('project')}>
                <Plus className="h-4 w-4 mr-2" />
                Add Category
              </Button>
            </div>
            <div className="rounded-md border">
              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-background z-10">
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Subcategories</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {projectCategories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell className="font-medium">{category.name}</TableCell>
                      <TableCell>{category.description || "-"}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {category.subcategories_names && category.subcategories_names.length > 0 ? (
                            category.subcategories_names.map((subName, index) => (
                              <Badge key={index} variant="outline" className="mr-1 mb-1">
                                {subName}
                              </Badge>
                            ))
                          ) : (
                            <span className="text-muted-foreground text-sm">No subcategories</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{new Date(category.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => openCategoryDialog('project', category)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteCategory(category.id, 'project')}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </div>
          </TabsContent>

          {/* Project Subcategories */}
          <TabsContent value="project-subcategories" className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Project Subcategories</h3>
                <p className="text-sm text-muted-foreground">Total: {projectSubcategories.length} subcategories</p>
              </div>
              <Button onClick={() => openSubcategoryDialog('project')}>
                <Plus className="h-4 w-4 mr-2" />
                Add Subcategory
              </Button>
            </div>
            <div className="rounded-md border">
              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-background z-10">
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {projectSubcategories.map((subcategory) => (
                    <TableRow key={subcategory.id}>
                      <TableCell className="font-medium">{subcategory.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{subcategory.category_name}</Badge>
                      </TableCell>
                      <TableCell>{subcategory.description || "-"}</TableCell>
                      <TableCell>{new Date(subcategory.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => openSubcategoryDialog('project', subcategory)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteSubcategory(subcategory.id, 'project')}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </div>
          </TabsContent>

          {/* Service Categories */}
          <TabsContent value="service-categories" className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Service Categories</h3>
                <p className="text-sm text-muted-foreground">Total: {serviceCategories.length} categories</p>
              </div>
              <Button onClick={() => openCategoryDialog('service')}>
                <Plus className="h-4 w-4 mr-2" />
                Add Category
              </Button>
            </div>
            <div className="rounded-md border">
              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-background z-10">
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Subcategories</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {serviceCategories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell className="font-medium">{category.name}</TableCell>
                      <TableCell>{category.description || "-"}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {category.subcategories_names && category.subcategories_names.length > 0 ? (
                            category.subcategories_names.map((subName, index) => (
                              <Badge key={index} variant="outline" className="mr-1 mb-1">
                                {subName}
                              </Badge>
                            ))
                          ) : (
                            <span className="text-muted-foreground text-sm">No subcategories</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{new Date(category.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => openCategoryDialog('service', category)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteCategory(category.id, 'service')}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </div>
          </TabsContent>

          {/* Service Subcategories */}
          <TabsContent value="service-subcategories" className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Service Subcategories</h3>
                <p className="text-sm text-muted-foreground">Total: {serviceSubcategories.length} subcategories</p>
              </div>
              <Button onClick={() => openSubcategoryDialog('service')}>
                <Plus className="h-4 w-4 mr-2" />
                Add Subcategory
              </Button>
            </div>
            <div className="rounded-md border">
              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-background z-10">
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {serviceSubcategories.map((subcategory) => (
                    <TableRow key={subcategory.id}>
                      <TableCell className="font-medium">{subcategory.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{subcategory.category_name}</Badge>
                      </TableCell>
                      <TableCell>{subcategory.description || "-"}</TableCell>
                      <TableCell>{new Date(subcategory.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => openSubcategoryDialog('service', subcategory)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteSubcategory(subcategory.id, 'service')}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* Category Dialog */}
        <Dialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingCategory ? "Edit Category" : "Add New Category"}
              </DialogTitle>
              <DialogDescription>
                {editingCategory 
                  ? "Update the category details below" 
                  : `Create a new ${currentCategoryType} category`
                }
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={categoryForm.handleSubmit(handleCategorySubmit)} className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Name</label>
                <Input {...categoryForm.register("name")} placeholder="Enter category name" />
                {categoryForm.formState.errors.name && (
                  <p className="text-sm text-destructive mt-1">
                    {categoryForm.formState.errors.name.message}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Description (Optional)</label>
                <Textarea {...categoryForm.register("description")} placeholder="Enter category description" rows={3} />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setCategoryDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={categoryForm.formState.isSubmitting}>
                  {categoryForm.formState.isSubmitting 
                    ? "Saving..." 
                    : editingCategory 
                      ? "Update Category" 
                      : "Create Category"
                  }
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>

        {/* Subcategory Dialog */}
        <Dialog open={subcategoryDialogOpen} onOpenChange={setSubcategoryDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingSubcategory ? "Edit Subcategory" : "Add New Subcategory"}
              </DialogTitle>
              <DialogDescription>
                {editingSubcategory 
                  ? "Update the subcategory details below" 
                  : `Create a new ${currentCategoryType} subcategory`
                }
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={subcategoryForm.handleSubmit(handleSubcategorySubmit)} className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Category</label>
                <Select 
                  value={subcategoryForm.watch("category")?.toString() || ""} 
                  onValueChange={(value) => {
                    if (value) {
                      subcategoryForm.setValue("category", parseInt(value));
                      subcategoryForm.clearErrors("category");
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {(currentCategoryType === 'project' ? projectCategories : serviceCategories).map((category) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {subcategoryForm.formState.errors.category && (
                  <p className="text-sm text-destructive mt-1">
                    {subcategoryForm.formState.errors.category.message}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Name</label>
                <Input {...subcategoryForm.register("name")} placeholder="Enter subcategory name" />
                {subcategoryForm.formState.errors.name && (
                  <p className="text-sm text-destructive mt-1">
                    {subcategoryForm.formState.errors.name.message}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Description (Optional)</label>
                <Textarea {...subcategoryForm.register("description")} placeholder="Enter subcategory description" rows={3} />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setSubcategoryDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={subcategoryForm.formState.isSubmitting}>
                  {subcategoryForm.formState.isSubmitting 
                    ? "Saving..." 
                    : editingSubcategory 
                      ? "Update Subcategory" 
                      : "Create Subcategory"
                  }
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
    </div>
  );
}
