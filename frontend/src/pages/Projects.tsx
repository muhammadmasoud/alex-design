import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useSearchParams } from "react-router-dom";
import SEO from "@/components/SEO";
import { api, endpoints, PaginatedResponse } from "@/lib/api";
import { Project } from "@/types";
import { Input } from "@/components/ui/input";
import { containerVariants, itemVariants } from "@/components/PageTransition";

// Lazy load components for better performance
const ProjectCard = lazy(() => import("@/components/ProjectCard"));
const PaginationControls = lazy(() => import("@/components/Pagination"));
const CategoryFilter = lazy(() => import("@/components/CategoryFilter"));
const Skeleton = lazy(() => import("@/components/ui/skeleton"));
const EmptyState = lazy(() => import("@/components/EmptyState"));

const PAGE_SIZE = 12;

export default function ProjectsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | undefined>();
  const [subcategory, setSubcategory] = useState<string | undefined>();
  const [categories, setCategories] = useState<string[]>([]);
  const [initializedFromURL, setInitializedFromURL] = useState(false);

  // Initialize state from URL parameters FIRST
  useEffect(() => {
    const categoryParam = searchParams.get('category');
    const subcategoryParam = searchParams.get('subcategory');
    const searchParam = searchParams.get('search');
    const pageParam = searchParams.get('page');

    if (categoryParam) setCategory(categoryParam);
    if (subcategoryParam) setSubcategory(subcategoryParam);
    if (searchParam) setSearch(searchParam);
    if (pageParam) setPage(parseInt(pageParam) || 1);
    
    setInitializedFromURL(true);
  }, [searchParams]);

  // Update URL when filters change
  const updateURL = (newCategory?: string, newSubcategory?: string, newSearch?: string, newPage?: number) => {
    const params = new URLSearchParams();
    
    if (newCategory) params.set('category', newCategory);
    if (newSubcategory) params.set('subcategory', newSubcategory);
    if (newSearch) params.set('search', newSearch);
    if (newPage && newPage > 1) params.set('page', newPage.toString());
    
    setSearchParams(params);
  };

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const { data } = await api.get(endpoints.categories.subcategories, {
          params: { type: 'project' }
        });
        setCategories(data.category_list?.map((cat: { value: string }) => cat.value) || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        // Fallback to default categories
        setCategories(["Residential", "Commercial", "Public", "Industrial", "Landscape", "Interior", "Urban", "Other"]);
      }
    };
    fetchCategories();
  }, []);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(count / PAGE_SIZE)), [count]);

  // Only fetch projects after URL initialization is complete
  useEffect(() => {
    if (!initializedFromURL) return; // Wait for URL initialization
    
    const fetchProjects = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log("Fetching projects with params:", { search, category, subcategory, page });
        const { data } = await api.get<PaginatedResponse<Project>>(endpoints.projects, {
          params: {
            search: search || undefined,
            category,
            subcategory,
            page,
            page_size: PAGE_SIZE,
          },
        });
        console.log("API Response:", data);
        const results = Array.isArray(data) ? data : data?.results || [];
        setItems(results);
        setCount(Array.isArray(data) ? results.length : data?.count || 0);
      } catch (e: unknown) {
        console.error("Error fetching projects:", e);
        setError(e instanceof Error ? e.message : "Failed to load projects");
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, [initializedFromURL, page, search, category, subcategory]);

     return (
     <motion.div 
       className="container py-8 sm:py-10 px-4 sm:px-6"
       variants={containerVariants}
       initial="hidden"
       animate="visible"
     >
       <SEO title="Projects | Studio Arc" description="Explore residential, commercial, and public architecture projects." canonical="/projects" />
       <motion.header className="mb-6" variants={itemVariants}>
         <h1 className="font-heading text-2xl sm:text-3xl">Projects</h1>
         <p className="mt-2 text-sm sm:text-base text-muted-foreground">Browse our portfolio with filters, search, and pagination.</p>
       </motion.header>

                 <motion.div className="flex flex-col sm:flex-row gap-4 mb-6" variants={itemVariants}>
           <div className="flex-1">
             <Input 
               value={search} 
               onChange={(e) => { 
                 const newSearch = e.target.value;
                 setPage(1); 
                 setSearch(newSearch);
                 updateURL(category, subcategory, newSearch || undefined, 1);
               }} 
               placeholder="Search projects"
               className="w-full" 
             />
           </div>
           <div className="sm:w-auto">
             <CategoryFilter
               categories={categories}
               category={category}
               subcategory={subcategory}
               onCategoryChange={(v) => { 
                 setPage(1); 
                 setCategory(v);
                 setSubcategory(undefined); // Reset subcategory when category changes
                 updateURL(v, undefined, search || undefined, 1);
               }}
               onSubcategoryChange={(v) => { 
                 setPage(1); 
                 setSubcategory(v);
                 updateURL(category, v, search || undefined, 1);
               }}
               type="project"
             />
           </div>
         </motion.div>

        {loading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-72 w-full" />
            ))}
          </div>
        ) : error ? (
          <EmptyState title="Couldn't load projects" description={error} />
        ) : items.length === 0 ? (
          <EmptyState title="No projects found" description="Try adjusting filters or search." />
        ) : (
          <>
                         <motion.section 
               className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
               variants={itemVariants}
             >
               {items.map((p, index) => (
                 <motion.div
                   key={p.id}
                   variants={itemVariants}
                   transition={{ delay: index * 0.1 }}
                 >
                   <ProjectCard project={p} />
                 </motion.div>
               ))}
             </motion.section>
             <motion.div className="mt-8 flex justify-center" variants={itemVariants}>
               <PaginationControls 
                 page={page} 
                 totalPages={totalPages} 
                 onPageChange={(newPage) => {
                   setPage(newPage);
                   updateURL(category, subcategory, search || undefined, newPage);
                 }} 
               />
             </motion.div>
          </>
        )}
         </motion.div>
   );
}
