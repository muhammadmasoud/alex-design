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
  category?: string;
  subcategory?: string;
  category_name?: string;
  subcategory_name?: string;
  album_images_count?: number;
  featured_album_images?: AlbumImage[];
}

export interface ServiceItem {
  id: number;
  name: string;
  description: string;
  icon: string; // This will contain the full URL from the backend
  price: number;
  category?: string;
  subcategory?: string;
  category_name?: string;
  subcategory_name?: string;
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
