import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useEffect, useState } from "react";
import { api, endpoints } from "@/lib/api";

interface Subcategory {
  value: string;
  label: string;
}

interface Props {
  category: string;
  subcategory?: string;
  onSubcategoryChange: (val?: string) => void;
  type?: 'project' | 'service';
}

export default function SubcategoryFilter({ category, subcategory, onSubcategoryChange, type = 'project' }: Props) {
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [loadingSubcategories, setLoadingSubcategories] = useState(false);

  // Fetch subcategories when category changes
  useEffect(() => {
    if (category) {
      setLoadingSubcategories(true);
      const fetchSubcategories = async () => {
        try {
          const { data } = await api.get(endpoints.categories.subcategories, {
            params: { category, type }
          });
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
  }, [category, type]);

  // Reset subcategory when subcategories change
  useEffect(() => {
    if (subcategory && !subcategories.some(sub => sub.value === subcategory)) {
      onSubcategoryChange(undefined);
    }
  }, [subcategories, subcategory, onSubcategoryChange]);

  return (
    <Select 
      value={subcategory ?? "all"} 
      onValueChange={(v) => onSubcategoryChange(v === "all" ? undefined : v)}
      disabled={loadingSubcategories || subcategories.length === 0}
    >
      <SelectTrigger>
        <SelectValue placeholder={
          loadingSubcategories ? "Loading..." : 
          subcategories.length === 0 ? "No subcategories" :
          "All Subcategories"
        } />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All Subcategories</SelectItem>
        {subcategories.map((sub) => (
          <SelectItem key={sub.value} value={sub.value}>{sub.label}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
