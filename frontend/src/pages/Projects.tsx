import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
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

const PAGE_SIZE = 6;

export default function ProjectsPage() {
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | undefined>();
  const [subcategory, setSubcategory] = useState<string | undefined>();
  const [categories, setCategories] = useState<string[]>([]);

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const { data } = await api.get(endpoints.categories.subcategories, {
          params: { type: 'project' }
        });
        setCategories(data.category_list?.map((cat: any) => cat.value) || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        // Fallback to default categories
        setCategories(["Residential", "Commercial", "Public", "Industrial", "Landscape", "Interior", "Urban", "Other"]);
      }
    };
    fetchCategories();
  }, []);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(count / PAGE_SIZE)), [count]);

  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await api.get<PaginatedResponse<Project>>(endpoints.projects, {
          params: {
            search: search || undefined,
            category,
            subcategory,
            page,
            page_size: PAGE_SIZE,
          },
        });
        const results = Array.isArray(data) ? data : data?.results || []; // Handle plain array or paginated response
        setItems(results);
        setCount(Array.isArray(data) ? results.length : data?.count || 0);
      } catch (e: any) {
        setError(e?.message || "Failed to load projects");
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, [page, search, category, subcategory]);

     return (
     <motion.div 
       className="container py-8 sm:py-10 px-4 sm:px-6"
       variants={containerVariants}
       initial="hidden"
       animate="visible"
     >
       <SEO 
         title="Architecture Projects | Alexandria Design Portfolio | Modern Residential & Commercial" 
         description="Explore our portfolio of modern architecture projects in Egypt. Residential homes, commercial buildings, interior design, and sustainable architecture by Alexandria Design studio."
         canonical="/projects"
         keywords="architecture projects Egypt, residential architecture, commercial buildings, interior design projects, modern architecture portfolio, Alexandria Design projects, sustainable buildings"
         structuredData={{
           "@context": "https://schema.org",
           "@type": "CollectionPage",
           "name": "Architecture Projects Portfolio",
           "description": "Portfolio of architecture projects by Alexandria Design",
           "mainEntity": {
             "@type": "ItemList",
             "name": "Architecture Projects",
             "description": "Collection of residential, commercial, and sustainable architecture projects"
           }
         }}
       />
       <motion.header className="mb-6" variants={itemVariants}>
         <h1 className="font-heading text-2xl sm:text-3xl">Projects</h1>
         <p className="mt-2 text-sm sm:text-base text-muted-foreground">Browse our portfolio with filters, search, and pagination.</p>
       </motion.header>

                 <motion.div className="flex flex-col sm:flex-row gap-4 mb-6" variants={itemVariants}>
           <div className="flex-1">
             <Input 
               value={search} 
               onChange={(e) => { setPage(1); setSearch(e.target.value); }} 
               placeholder="Search projects"
               className="w-full" 
             />
           </div>
           <div className="sm:w-auto">
             <CategoryFilter
               categories={categories}
               category={category}
               subcategory={subcategory}
               onCategoryChange={(v) => { setPage(1); setCategory(v); }}
               onSubcategoryChange={(v) => { setPage(1); setSubcategory(v); }}
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
               <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />
             </motion.div>
          </>
        )}
         </motion.div>
   );
}
