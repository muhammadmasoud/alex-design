import { useEffect, useState, lazy, Suspense } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, BarChart3, Settings, ImageIcon, FileText, FolderOpen } from "lucide-react";
import SEO from "@/components/SEO";
import ProtectedRoute from "@/components/ProtectedRoute";
import { Skeleton } from "@/components/ui/skeleton";

// Lazy load admin components since they're heavy and only used by admins
const ProjectManagement = lazy(() => import("@/components/admin/ProjectManagement"));
const ServiceManagement = lazy(() => import("@/components/admin/ServiceManagement"));
const CategoryManagement = lazy(() => import("@/components/admin/CategoryManagement"));
const AdminStats = lazy(() => import("@/components/admin/AdminStats"));

interface DashboardData {
  user: {
    id: number;
    username: string;
    email: string;
    is_superuser: boolean;
    is_staff: boolean;
  };
  statistics: {
    projects_count: number;
    services_count: number;
    storage: {
      media_size_mb: number;
      media_file_count: number;
      disk_total_gb: number;
      disk_free_gb: number;
      disk_used_gb: number;
      disk_usage_percent: number;
    };
  };
  recent_projects: any[];
  categories: {
    projects: Record<string, any[]>;
    services: Record<string, any[]>;
  };
}

export default function AdminDashboard() {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("projects");

  const fetchDashboardData = async () => {
    if (!isAuthenticated || !isAdmin) return;
    
    try {
      const response = await api.get(endpoints.admin.dashboard);
      setDashboardData(response.data);
    } catch (error: any) {
      console.error("Error fetching dashboard data:", error);
      
      // Check if it's a 500 error
      if (error.response?.status === 500) {
        console.error("Server error details:", error.response.data);
        toast({
          title: "Server Error",
          description: "The server encountered an error while loading dashboard data. Please try again or contact support.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Error",
          description: error.response?.data?.detail || "Failed to load dashboard data",
          variant: "destructive",
        });
      }
      
      // Set a fallback dashboard data to prevent the component from crashing
      setDashboardData({
        user: {
          id: 0,
          username: 'Unknown',
          email: '',
          is_superuser: false,
          is_staff: false
        },
        statistics: {
          projects_count: 0,
          services_count: 0,
          storage: {
            media_size_mb: 0,
            media_file_count: 0,
            disk_total_gb: 0,
            disk_free_gb: 0,
            disk_used_gb: 0,
            disk_usage_percent: 0
          }
        },
        recent_projects: [],
        categories: {
          projects: {},
          services: {}
        }
      });
    }
  };

  useEffect(() => {
    const initializeDashboard = async () => {
      if (!loading) {
        await fetchDashboardData();
        setIsLoading(false);
      }
    };

    initializeDashboard();
  }, [isAuthenticated, isAdmin, loading]);

  const handleDataUpdate = async () => {
    // Refresh only the dashboard statistics without reloading the page
    try {
      const response = await api.get(endpoints.admin.dashboard);
      setDashboardData(response.data);
    } catch (error: any) {
      console.error("Error refreshing dashboard data:", error);
      
      // Check if it's a 500 error
      if (error.response?.status === 500) {
        console.error("Server error details:", error.response.data);
        toast({
          title: "Dashboard Update Error",
          description: "Failed to refresh dashboard data. The server encountered an error.",
          variant: "destructive",
        });
      }
      
      // Don't show error toast here since components handle their own errors
    }
  };

  const handleStorageUpdate = async () => {
    // Update only storage statistics for better performance
    if (!dashboardData) return;
    
    try {
      const response = await api.get(endpoints.admin.storageStats);
      setDashboardData(prev => prev ? {
        ...prev,
        statistics: {
          ...prev.statistics,
          storage: response.data.storage
        }
      } : null);
    } catch (error: any) {
      console.error("Error refreshing storage data:", error);
      
      // Check if it's a 500 error
      if (error.response?.status === 500) {
        console.error("Server error details:", error.response.data);
        toast({
          title: "Storage Update Error",
          description: "Failed to update storage statistics. The server encountered an error.",
          variant: "destructive",
        });
      }
      
      // Fallback to full dashboard refresh
      handleDataUpdate();
    }
  };

  if (loading || isLoading) {
    return (
      <div className="container py-10">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p>Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="container py-10">
        <div className="text-center">
          <p>Failed to load dashboard data</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute requireAdmin={true}>
      <div className="container py-8">
        <SEO 
          title="Admin Dashboard | Alex Design" 
          description="Administrative dashboard for managing projects and services"
          canonical="/admin"
        />
        
        <div className="mb-8">
          <h1 className="font-heading text-3xl mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {dashboardData.user.username}! Manage your projects and services here.
          </p>
        </div>

        <Suspense fallback={
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-48" />
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-20 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        }>
          <AdminStats statistics={dashboardData.statistics} />
        </Suspense>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="projects" className="flex items-center gap-2">
              <ImageIcon className="h-4 w-4" />
              Projects
            </TabsTrigger>
            <TabsTrigger value="services" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Services
            </TabsTrigger>
            <TabsTrigger value="categories" className="flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Categories
            </TabsTrigger>
          </TabsList>

          <TabsContent value="projects" className="mt-6">
            <Suspense fallback={
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            }>
              <ProjectManagement 
                onUpdate={handleDataUpdate}
                onStorageUpdate={handleStorageUpdate}
              />
            </Suspense>
          </TabsContent>

          <TabsContent value="services" className="mt-6">
            <Suspense fallback={
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            }>
              <ServiceManagement 
                onUpdate={handleDataUpdate}
                onStorageUpdate={handleStorageUpdate}
              />
            </Suspense>
          </TabsContent>

          <TabsContent value="categories" className="mt-6">
            <Suspense fallback={
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            }>
              <CategoryManagement 
                onUpdate={handleDataUpdate}
              />
            </Suspense>
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  );
}
