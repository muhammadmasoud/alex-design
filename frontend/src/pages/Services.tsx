import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import SEO from "@/components/SEO";
import { api, endpoints, PaginatedResponse } from "@/lib/api";
import { ServiceItem } from "@/types";
import { containerVariants, itemVariants } from "@/components/PageTransition";

const ServiceCard = lazy(() => import("@/components/ServiceCard"));
const PaginationControls = lazy(() => import("@/components/Pagination"));
const CategoryFilter = lazy(() => import("@/components/CategoryFilter"));
const Skeleton = lazy(() => import("@/components/ui/skeleton"));
const EmptyState = lazy(() => import("@/components/EmptyState"));

const PAGE_SIZE = 12;

export default function ServicesPage() {
  const [items, setItems] = useState<ServiceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [category, setCategory] = useState<string | undefined>();
  const [subcategory, setSubcategory] = useState<string | undefined>();
  const [categories, setCategories] = useState<string[]>([]);

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const { data } = await api.get(endpoints.categories.subcategories, {
          params: { type: 'service' }
        });
        setCategories(data.category_list?.map((cat: any) => cat.value) || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        // Fallback to default categories
        setCategories(["Design", "Planning", "Consulting", "Visualization"]);
      }
    };
    fetchCategories();
  }, []);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(count / PAGE_SIZE)), [count]);

  useEffect(() => {
    const fetchServices = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await api.get<PaginatedResponse<ServiceItem>>(endpoints.services, {
          params: {
            category,
            subcategory,
            page,
            page_size: PAGE_SIZE,
          },
        });
        setItems(data.results);
        setCount(data.count);
      } catch (e: any) {
        setError(e?.message || "Failed to load services");
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, [page, category, subcategory]);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="container py-10">
        <SEO title="Services | Studio Arc" description="Architectural design, planning, consulting, and visualization services." canonical="/services" />
        <header className="mb-6">
          <h1 className="font-heading text-3xl">Services</h1>
          <p className="mt-2 text-muted-foreground">What we offer to bring your vision to life.</p>
        </header>

        <div className="mb-6 max-w-sm">
          <CategoryFilter
            categories={categories}
            category={category}
            subcategory={subcategory}
            onCategoryChange={(v) => { setPage(1); setCategory(v); }}
            onSubcategoryChange={(v) => { setPage(1); setSubcategory(v); }}
            type="service"
          />
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-64 w-full" />
            ))}
          </div>
        ) : error ? (
          <EmptyState title="Couldn't load services" description={error} />
        ) : items.length === 0 ? (
          <EmptyState title="No services found" description="Try a different category." />
        ) : (
          <>
            <section className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((s) => (
                <ServiceCard key={s.id} item={s} />
              ))}
            </section>
            <div className="mt-8 flex justify-center">
              <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
      </div>
    </Suspense>
  );
}
