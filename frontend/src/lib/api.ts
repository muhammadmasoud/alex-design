
import axios from "axios";

export const API_BASE_URL = "/api"; // Use proxy for local development

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for CSRF cookies
  timeout: 900000, // 15 minutes timeout for large file uploads (increased from 5 minutes)
});

// Function to get CSRF token
const getCSRFToken = () => {
  // Try to get from meta tag first
  const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (metaToken) return metaToken;
  
  // Fallback to cookie
  const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  return token;
};

// Function to initialize CSRF token
const initializeCSRFToken = async () => {
  try {
    const response = await axios.get('/api/csrf-token/', { withCredentials: true });
    // Token will be set in cookie automatically by Django
    return response.data.csrfToken;
  } catch (error) {
    console.warn('Failed to initialize CSRF token:', error);
    return null;
  }
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    const headers = (config.headers ?? {}) as Record<string, any>;
    headers.Authorization = `Token ${token}`;
    config.headers = headers as any;
  }
  
  // Add CSRF token for POST/PUT/DELETE requests
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      const headers = (config.headers ?? {}) as Record<string, any>;
      headers['X-CSRFToken'] = csrfToken;
      config.headers = headers as any;
    }
  }
  
  // Set Content-Type only if it's not FormData
  if (!(config.data instanceof FormData)) {
    const headers = (config.headers ?? {}) as Record<string, any>;
    headers["Content-Type"] = "application/json";
    config.headers = headers as any;
  }
  
  return config;
});

// Initialize CSRF token when the module loads
initializeCSRFToken();

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const endpoints = {
  projects: "/projects/",
  projectDetail: (id: string | number) => `/projects/${id}/`,
  projectAlbum: (id: string | number) => `/projects/${id}/album/`,
  projectImages: "/project-images/",
  projectImagesBulkUpload: "/project-images/bulk_upload/",
  services: "/services/",
  serviceDetail: (id: string | number) => `/services/${id}/`,
  serviceAlbum: (id: string | number) => `/services/${id}/album/`,
  serviceImages: "/service-images/",
  serviceImagesBulkUpload: "/service-images/bulk_upload/",
  auth: {
    login: "/auth/login/",
    register: "/auth/register/",
  },
  admin: {
    dashboard: "/admin/dashboard/",
    storageStats: "/admin/storage-stats/",
    check: "/admin/check/",
    projects: "/admin/projects/",
    services: "/admin/services/",
    projectCategories: "/admin/project-categories/",
    projectSubcategories: "/admin/project-subcategories/",
    serviceCategories: "/admin/service-categories/",
    serviceSubcategories: "/admin/service-subcategories/",
    consultationSettings: "/admin/consultation-settings/",
    daysOff: "/admin/days-off/",
    bookings: "/admin/bookings/",
  },
  contact: "/contact/",
  categories: {
    subcategories: "/categories/subcategories/",
  },
  consultations: {
    book: "/consultations/book/",
    availableSlots: "/consultations/available-slots/",
    settings: "/consultations/settings/",
    daysOff: "/consultations/days-off/",
    checkMonthly: "/consultations/check-monthly/",
  },
};

export const fetchProjects = async () => {
  try {
    const response = await api.get(endpoints.projects);
    return response.data;
  } catch (error) {
    console.error("Error fetching projects:", error);
    throw error;
  }
};
