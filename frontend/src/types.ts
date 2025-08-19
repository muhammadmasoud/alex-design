export interface AlbumImage {
  id: number;
  image: string;
  image_url: string;
  title?: string;
  description?: string;
  order: number;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  image: string; // This will contain the full URL from the backend
  project_date: string; // The manually entered project date
  categories?: number[]; // Array of category IDs for form submission
  subcategories?: number[]; // Array of subcategory IDs for form submission
  category_names?: string[]; // Array of category names from API
  subcategory_names?: string[]; // Array of subcategory names from API
  category_name?: string; // First category name for backward compatibility
  subcategory_name?: string; // First subcategory name for backward compatibility
  album_images_count?: number;
  featured_album_images?: AlbumImage[];
}

export interface ServiceItem {
  id: number;
  name: string;
  description: string;
  icon: string; // This will contain the full URL from the backend
  price: number;
  categories?: number[]; // Array of category IDs for form submission
  subcategories?: number[]; // Array of subcategory IDs for form submission
  category_names?: string[]; // Array of category names from API
  subcategory_names?: string[]; // Array of subcategory names from API
  category_name?: string; // First category name for backward compatibility
  subcategory_name?: string; // First subcategory name for backward compatibility
  album_images_count?: number;
  featured_album_images?: AlbumImage[];
}

export interface ProjectAlbumResponse {
  project: {
    id: number;
    title: string;
    description: string;
    image: string | null;
    category_name: string | null;
    subcategory_name: string | null;
  };
  album_images: AlbumImage[];
  total_images: number;
}

export interface ServiceAlbumResponse {
  service: {
    id: number;
    name: string;
    description: string;
    icon: string | null;
    price: string;
    category_name: string | null;
    subcategory_name: string | null;
  };
  album_images: AlbumImage[];
  total_images: number;
}
