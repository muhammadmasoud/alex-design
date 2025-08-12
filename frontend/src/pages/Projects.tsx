import { Suspense, useEffect, useMemo, useState } from "react";
import SEO from "@/components/SEO";
import { api, endpoints, PaginatedResponse } from "@/lib/api";
import { Project } from "@/types";
import ProjectCard from "@/components/ProjectCard";
import PaginationControls from "@/components/Pagination";
import CategoryFilter from "@/components/CategoryFilter";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/EmptyState";

const PAGE_SIZE = 12;

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
        console.log("Full API Response:", data); // Log full response
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
    <div className="container py-10">
      <SEO title="Projects | Studio Arc" description="Explore residential, commercial, and public architecture projects." canonical="/projects" />
      <header className="mb-6">
        <h1 className="font-heading text-3xl">Projects</h1>
        <p className="mt-2 text-muted-foreground">Browse our portfolio with filters, search, and pagination.</p>
      </header>

        <div className="grid gap-4 sm:grid-cols-[1fr_auto] items-end mb-6">
          <Input value={search} onChange={(e) => { setPage(1); setSearch(e.target.value); }} placeholder="Search projects" />
          <CategoryFilter
            categories={categories}
            category={category}
            subcategory={subcategory}
            onCategoryChange={(v) => { setPage(1); setCategory(v); }}
            onSubcategoryChange={(v) => { setPage(1); setSubcategory(v); }}
            type="project"
          />
        </div>

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
            <section className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((p) => (
                <ProjectCard key={p.id} project={p} />
              ))}
            </section>
            <div className="mt-8 flex justify-center">
              <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
    </div>
  );
}
