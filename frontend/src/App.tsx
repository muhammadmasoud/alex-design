import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RootLayout from "@/layouts/RootLayout";
import { lazy, Suspense } from "react";
import { AuthProvider } from "@/contexts/AuthContext";

const Index = lazy(() => import("./pages/Index"));
const ProjectsPage = lazy(() => import("./pages/Projects"));
const ProjectDetail = lazy(() => import("./pages/ProjectDetail"));
const ServicesPage = lazy(() => import("./pages/Services"));
const ServiceDetail = lazy(() => import("./pages/ServiceDetail"));
const LoginPage = lazy(() => import("./pages/Login"));
const RegisterPage = lazy(() => import("./pages/Register"));
const ContactPage = lazy(() => import("./pages/Contact"));
const AboutPage = lazy(() => import("./pages/About"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const GalleryDemo = lazy(() => import("./pages/GalleryDemo"));
const NotFound = lazy(() => import("./pages/NotFound"));

import { ThemeProvider } from "./components/theme-provider";
import ResourcePreloader from "./components/ResourcePreloader";
import PageTransition, { LoadingPageTransition } from "./components/PageTransition";
import heroImage from "@/assets/hero-architecture.jpg";

const queryClient = new QueryClient();

const App = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AuthProvider>
          <ResourcePreloader 
            images={[heroImage]} 
          />
          <Toaster />
          <Sonner />
          <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true,
            }}
          >
                         <Suspense fallback={<LoadingPageTransition />}>
              <Routes>
                <Route path="/" element={<RootLayout />}>
                                     <Route index element={<Index />} />
                   <Route path="projects" element={<ProjectsPage />} />
                   <Route path="projects/:id" element={<ProjectDetail />} />
                   <Route path="services" element={<ServicesPage />} />
                   <Route path="services/:id" element={<ServiceDetail />} />
                   <Route path="about" element={<AboutPage />} />
                   <Route path="login" element={<LoginPage />} />
                   <Route path="register" element={<RegisterPage />} />
                   <Route path="contact" element={<ContactPage />} />
                   <Route path="admin-dashboard" element={<AdminDashboard />} />
                   <Route path="gallery-demo" element={<GalleryDemo />} />
                   <Route path="*" element={<NotFound />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  </ThemeProvider>
);

export default App;
