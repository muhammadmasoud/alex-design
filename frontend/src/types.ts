export interface AlbumImage {
  id: number;
  image: string;
  image_url: string;
  original_image_url?: string;
  title?: string;
  description?: string;
  order: number;
  original_filename?: string;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  image: string; // This will contain the full URL from the backend
  original_image_url?: string; // Original unoptimized image URL for lightbox
  project_date: string; // The manually entered project date
  categories?: number[]; // Array of category IDs for form submission
  subcategories?: number[]; // Array of subcategory IDs for form submission
  category_names?: string[]; // Array of category names from API
  subcategory_names?: string[]; // Array of subcategory names from API
  category_name?: string; // First category name for backward compatibility
  subcategory_name?: string; // First subcategory name for backward compatibility
  album_images_count?: number;
  featured_album_images?: AlbumImage[];
  original_filename?: string;
}

export interface ServiceItem {
  id: number;
  name: string;
  description: string;
  icon: string; // This will contain the full URL from the backend
  original_image_url?: string; // Original unoptimized icon URL for lightbox
  original_icon_url?: string; // Alternative field name for original icon
  price: number;
  categories?: number[]; // Array of category IDs for form submission
  subcategories?: number[]; // Array of subcategory IDs for form submission
  category_names?: string[]; // Array of category names from API
  subcategory_names?: string[]; // Array of subcategory names from API
  category_name?: string; // First category name for backward compatibility
  subcategory_name?: string; // First subcategory name for backward compatibility
  album_images_count?: number;
  featured_album_images?: AlbumImage[];
  original_filename?: string;
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

// Consultation Booking Types
export interface ConsultationSettings {
  id?: number;
  meeting_duration_minutes: number;
  buffer_time_minutes: number;
  monday_hours: string;
  tuesday_hours: string;
  wednesday_hours: string;
  thursday_hours: string;
  friday_hours: string;
  saturday_hours: string;
  sunday_hours: string;
  booking_enabled: boolean;
  advance_booking_days: number;
  minimum_notice_hours: number;
  created_at?: string;
  updated_at?: string;
}

export interface PublicConsultationSettings {
  booking_enabled: boolean;
  meeting_duration_minutes: number;
  advance_booking_days: number;
  minimum_notice_hours: number;
  working_hours: {
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
    sunday: string;
  };
}

export interface DayOff {
  id?: number;
  date: string;
  reason?: string;
  created_at?: string;
}

export interface Booking {
  id?: number;
  client_name: string;
  client_email: string;
  client_phone?: string;
  date: string;
  time: string;
  end_time?: string;
  duration_minutes: number;
  project_details?: string;
  message?: string;
  status?: 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no_show';
  admin_notes?: string;
  is_past?: boolean;
  can_be_cancelled?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PublicBookingData {
  client_name: string;
  client_email: string;
  client_phone?: string;
  date: string;
  time: string;
  duration_minutes?: number;
  project_details?: string;
  message?: string;
}

export interface AvailableSlots {
  date: string;
  available_slots: string[];
  total_slots: number;
}
