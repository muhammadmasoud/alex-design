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
      <motion.div 
        className="container py-8 sm:py-10 px-4 sm:px-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <SEO 
          title="Architecture Services | Alexandria Design | Egypt | Residential & Commercial Design"
          description="Professional architectural services in Egypt: Architectural design, interior design, site supervision, green architecture, furniture manufacturing. Expert architects serving Alexandria and Egypt."
          canonical="/services"
          keywords="architectural services Egypt, architecture design services, interior design services, site supervision, green architecture Egypt, furniture manufacturing, Alexandria architects"
          structuredData={{
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "Architectural Services",
            "provider": {
              "@type": "Organization",
              "name": "Alexandria Design"
            },
            "areaServed": {
              "@type": "Place",
              "name": "Egypt"
            },
            "hasOfferCatalog": {
              "@type": "OfferCatalog",
              "name": "Architecture Services",
              "itemListElement": [
                {
                  "@type": "Offer",
                  "itemOffered": {
                    "@type": "Service",
                    "name": "Architectural Design"
                  }
                },
                {
                  "@type": "Offer", 
                  "itemOffered": {
                    "@type": "Service",
                    "name": "Interior Design"
                  }
                },
                {
                  "@type": "Offer",
                  "itemOffered": {
                    "@type": "Service", 
                    "name": "Site Supervision"
                  }
                }
              ]
            }
          }}
        />
        <motion.header className="mb-6" variants={itemVariants}>
          <h1 className="font-heading text-2xl sm:text-3xl">Services</h1>
          <p className="mt-2 text-sm sm:text-base text-muted-foreground">What we offer to bring your vision to life.</p>
        </motion.header>

        <motion.div className="mb-6 w-full sm:max-w-sm" variants={itemVariants}>
          <CategoryFilter
            categories={categories}
            category={category}
            subcategory={subcategory}
            onCategoryChange={(v) => { setPage(1); setCategory(v); }}
            onSubcategoryChange={(v) => { setPage(1); setSubcategory(v); }}
            type="service"
          />
        </motion.div>

        {loading ? (
          <motion.div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3" variants={itemVariants}>
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-64 w-full" />
            ))}
          </motion.div>
        ) : error ? (
          <motion.div variants={itemVariants}>
            <EmptyState title="Couldn't load services" description={error} />
          </motion.div>
        ) : items.length === 0 ? (
          <motion.div variants={itemVariants}>
            <EmptyState title="No services found" description="Try a different category." />
          </motion.div>
        ) : (
          <>
            <motion.section className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3" variants={itemVariants}>
              {items.map((s, index) => (
                <motion.div
                  key={s.id}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <ServiceCard item={s} />
                </motion.div>
              ))}
            </motion.section>
            <motion.div className="mt-8 flex justify-center" variants={itemVariants}>
              <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />
            </motion.div>
          </>
        )}
      </motion.div>
    </Suspense>
  );
}
