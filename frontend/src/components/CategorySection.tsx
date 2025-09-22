import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { api, endpoints, PaginatedResponse } from "@/lib/api";
import { Project } from "@/types";
import { Input } from "@/components/ui/input";
import { itemVariants } from "@/components/PageTransition";

// Lazy load components for better performance
const ProjectCard = lazy(() => import("@/components/ProjectCard"));
const PaginationControls = lazy(() => import("@/components/Pagination"));
const SubcategoryFilter = lazy(() => import("@/components/SubcategoryFilter"));
const Skeleton = lazy(() => import("@/components/ui/skeleton"));
const EmptyState = lazy(() => import("@/components/EmptyState"));

const PAGE_SIZE = 6;

interface CategorySectionProps {
  categoryName: string;
  displayTitle: string;
  description: string;
}

export default function CategorySection({ categoryName, displayTitle, description }: CategorySectionProps) {
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [search, setSearch] = useState("");
  const [subcategory, setSubcategory] = useState<string | undefined>();

  const totalPages = useMemo(() => Math.max(1, Math.ceil(count / PAGE_SIZE)), [count]);

  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await api.get<PaginatedResponse<Project>>(endpoints.projects, {
          params: {
            search: search || undefined,
            category: categoryName,
            subcategory,
            page,
            page_size: PAGE_SIZE,
          },
        });
        const results = Array.isArray(data) ? data : data?.results || [];
        setItems(results);
        setCount(Array.isArray(data) ? results.length : data?.count || 0);
      } catch (e: any) {
        setError(e?.message || "Failed to load projects");
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, [page, search, categoryName, subcategory]);

  return (
    <motion.section 
      className="mb-12"
      variants={itemVariants}
    >
      {/* Section Header */}
      <motion.div className="mb-6" variants={itemVariants}>
        <h2 className="font-heading text-xl sm:text-2xl mb-2">{displayTitle}</h2>
        <p className="text-sm sm:text-base text-muted-foreground">{description}</p>
      </motion.div>

      {/* Filters */}
      <motion.div className="flex flex-col sm:flex-row gap-4 mb-6" variants={itemVariants}>
        <div className="flex-1">
          <Input 
            value={search} 
            onChange={(e) => { setPage(1); setSearch(e.target.value); }} 
            placeholder={`Search ${displayTitle.toLowerCase()}`}
            className="w-full" 
          />
        </div>
        <div className="sm:w-64">
          <Suspense fallback={<div>Loading filters...</div>}>
            <SubcategoryFilter
              category={categoryName}
              subcategory={subcategory}
              onSubcategoryChange={(v) => { setPage(1); setSubcategory(v); }}
              type="project"
            />
          </Suspense>
        </div>
      </motion.div>

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Suspense key={i} fallback={<div>Loading...</div>}>
              <Skeleton className="h-72 w-full" />
            </Suspense>
          ))}
        </div>
      ) : error ? (
        <Suspense fallback={<div>Loading...</div>}>
          <EmptyState title="Couldn't load projects" description={error} />
        </Suspense>
      ) : items.length === 0 ? (
        <Suspense fallback={<div>Loading...</div>}>
          <EmptyState title="No projects found" description="Try adjusting filters or search." />
        </Suspense>
      ) : (
        <>
          <motion.div 
            className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8"
            variants={itemVariants}
          >
            {items.map((p, index) => (
              <motion.div
                key={p.id}
                variants={itemVariants}
                transition={{ delay: index * 0.1 }}
              >
                <Suspense fallback={<Skeleton className="h-72 w-full" />}>
                  <ProjectCard project={p} />
                </Suspense>
              </motion.div>
            ))}
          </motion.div>
          
          {totalPages > 1 && (
            <motion.div className="flex justify-center" variants={itemVariants}>
              <Suspense fallback={<div>Loading pagination...</div>}>
                <PaginationControls 
                  page={page} 
                  totalPages={totalPages} 
                  onPageChange={setPage} 
                />
              </Suspense>
            </motion.div>
          )}
        </>
      )}
    </motion.section>
  );
}
