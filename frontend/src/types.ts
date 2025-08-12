export interface Project {
  id: number;
  title: string;
  description: string;
  image: string; // This will contain the full URL from the backend
  created_at: string;
  category?: string;
  subcategory?: string;
}

export interface ServiceItem {
  id: number;
  name: string;
  description: string;
  icon: string; // This will contain the full URL from the backend
  price: number;
  category?: string;
}
