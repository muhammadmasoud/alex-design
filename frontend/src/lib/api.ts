import axios from "axios";

export const API_BASE_URL = "/api"; // Use proxy for local development

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for CSRF cookies
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

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    const headers = (config.headers ?? {}) as Record<string, any>;
    headers.Authorization = `Token ${token}`;
    config.headers = headers as any;
  }
  
  // CSRF TOKEN SENDING DISABLED - CAUSES LOGIN/REGISTRATION ERRORS
  // The following code is commented out to prevent CSRF token issues:
  /*
  // Add CSRF token for POST/PUT/DELETE requests
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      const headers = (config.headers ?? {}) as Record<string, any>;
      headers['X-CSRFToken'] = csrfToken;
      config.headers = headers as any;
    }
  }
  */
  
  // Set Content-Type only if it's not FormData
  if (!(config.data instanceof FormData)) {
    const headers = (config.headers ?? {}) as Record<string, any>;
    headers["Content-Type"] = "application/json";
    config.headers = headers as any;
  }
  
  return config;
});

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const endpoints = {
  projects: "/projects/",
  services: "/services/",
  auth: {
    login: "/auth/login/",
    register: "/auth/register/",
  },
  admin: {
    dashboard: "/admin/dashboard/",
    check: "/admin/check/",
    projectCategories: "/admin/project-categories/",
    projectSubcategories: "/admin/project-subcategories/",
    serviceCategories: "/admin/service-categories/",
    serviceSubcategories: "/admin/service-subcategories/",
  },
  contact: "/contact/",
  categories: {
    subcategories: "/categories/subcategories/",
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
