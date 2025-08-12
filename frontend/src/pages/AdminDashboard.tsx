import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, BarChart3, Settings, ImageIcon, FileText, FolderOpen } from "lucide-react";
import SEO from "@/components/SEO";
import ProtectedRoute from "@/components/ProtectedRoute";
import ProjectManagement from "@/components/admin/ProjectManagement";
import ServiceManagement from "@/components/admin/ServiceManagement";
import CategoryManagement from "@/components/admin/CategoryManagement";
import AdminStats from "@/components/admin/AdminStats";

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
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive",
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
    } catch (error) {
      console.error("Error refreshing dashboard data:", error);
      // Don't show error toast here since components handle their own errors
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

        <AdminStats statistics={dashboardData.statistics} />

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
            <ProjectManagement 
              onUpdate={handleDataUpdate}
            />
          </TabsContent>

          <TabsContent value="services" className="mt-6">
            <ServiceManagement 
              onUpdate={handleDataUpdate}
            />
          </TabsContent>

          <TabsContent value="categories" className="mt-6">
            <CategoryManagement 
              onUpdate={handleDataUpdate}
            />
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  );
}
