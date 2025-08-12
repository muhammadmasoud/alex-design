import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useEffect, useState } from "react";
import { api, endpoints } from "@/lib/api";

interface Subcategory {
  value: string;
  label: string;
}

interface Props {
  categories: string[];
  category?: string;
  subcategory?: string;
  onCategoryChange: (val?: string) => void;
  onSubcategoryChange: (val?: string) => void;
  type?: 'project' | 'service'; // Add type prop
}

export default function CategoryFilter({ categories, category, subcategory, onCategoryChange, onSubcategoryChange, type = 'project' }: Props) {
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [loadingSubcategories, setLoadingSubcategories] = useState(false);

  // Fetch subcategories when category changes
  useEffect(() => {
    if (category) {
      console.log('Fetching subcategories for category:', category);
      setLoadingSubcategories(true);
      const fetchSubcategories = async () => {
        try {
          console.log('Making API call to:', endpoints.categories.subcategories);
          const { data } = await api.get(endpoints.categories.subcategories, {
            params: { category, type }
          });
          console.log('Received subcategories:', data);
          setSubcategories(data.subcategories || []);
        } catch (error) {
          console.error('Failed to fetch subcategories:', error);
          setSubcategories([]);
        } finally {
          setLoadingSubcategories(false);
        }
      };
      fetchSubcategories();
    } else {
      setSubcategories([]);
    }
  }, [category]);

  // Reset subcategory when category changes
  useEffect(() => {
    if (subcategory && !subcategories.some(sub => sub.value === subcategory)) {
      onSubcategoryChange(undefined);
    }
  }, [subcategories, subcategory, onSubcategoryChange]);

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Select value={category ?? "all"} onValueChange={(v) => onCategoryChange(v === "all" ? undefined : v)}>
        <SelectTrigger>
          <SelectValue placeholder="Category" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Categories</SelectItem>
          {categories.map((c) => (
            <SelectItem key={c} value={c}>{c}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      <Select 
        value={subcategory ?? "all"} 
        onValueChange={(v) => onSubcategoryChange(v === "all" ? undefined : v)}
        disabled={!category || loadingSubcategories || subcategories.length === 0}
      >
        <SelectTrigger>
          <SelectValue placeholder={
            !category ? "Select category first" : 
            loadingSubcategories ? "Loading..." : 
            subcategories.length === 0 ? "No subcategories" :
            "Subcategory"
          } />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Subcategories</SelectItem>
          {subcategories.map((sub) => (
            <SelectItem key={sub.value} value={sub.value}>{sub.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
