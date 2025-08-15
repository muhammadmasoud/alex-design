import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, Grid3X3, Grid2X2, List, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import OptimizedImage, { ImagePresets } from './OptimizedImage';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';

interface GalleryItem {
  id: string;
  src: string;
  alt: string;
  title?: string;
  category?: string;
  description?: string;
  featured?: boolean;
}

interface GalleryGridProps {
  items: GalleryItem[];
  columns?: 2 | 3 | 4;
  aspectRatio?: string;
  enableFilter?: boolean;
  enableLightbox?: boolean;
  enableLayoutToggle?: boolean;
  className?: string;
  masonry?: boolean;
}

type LayoutType = 'grid-2' | 'grid-3' | 'grid-4' | 'masonry' | 'list';

export default function GalleryGrid({
  items,
  columns = 3,
  aspectRatio = "4/3",
  enableFilter = true,
  enableLightbox = true,
  enableLayoutToggle = true,
  className,
  masonry = false
}: GalleryGridProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [layout, setLayout] = useState<LayoutType>(`grid-${columns}` as LayoutType);
  
  // Extract unique categories
  const categories = ['all', ...Array.from(new Set(items.map(item => item.category).filter(Boolean)))];
  
  // Filter items
  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter(item => item.category === selectedCategory);

  // Layout configurations
  const layoutConfigs = {
    'grid-2': 'grid-cols-1 sm:grid-cols-2',
    'grid-3': 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3', 
    'grid-4': 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    'masonry': 'columns-1 sm:columns-2 lg:columns-3',
    'list': 'grid-cols-1'
  };

  const getItemHeight = (index: number) => {
    if (!masonry) return aspectRatio;
    // Varied heights for masonry layout
    const heights = ['300px', '400px', '350px', '450px', '320px'];
    return heights[index % heights.length];
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Controls */}
      {(enableFilter || enableLayoutToggle) && (
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          {/* Category Filter */}
          {enableFilter && categories.length > 1 && (
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  className="capitalize"
                >
                  {category}
                </Button>
              ))}
            </div>
          )}

          {/* Layout Toggle */}
          {enableLayoutToggle && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground mr-2">Layout:</span>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    {layout === 'grid-2' && <Grid2X2 className="h-4 w-4" />}
                    {layout === 'grid-3' && <Grid3X3 className="h-4 w-4" />}
                    {layout === 'grid-4' && <Grid3X3 className="h-4 w-4" />}
                    {layout === 'masonry' && <Filter className="h-4 w-4" />}
                    {layout === 'list' && <List className="h-4 w-4" />}
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setLayout('grid-2')}>
                    <Grid2X2 className="h-4 w-4 mr-2" /> 2 Columns
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLayout('grid-3')}>
                    <Grid3X3 className="h-4 w-4 mr-2" /> 3 Columns
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLayout('grid-4')}>
                    <Grid3X3 className="h-4 w-4 mr-2" /> 4 Columns
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLayout('masonry')}>
                    <Filter className="h-4 w-4 mr-2" /> Masonry
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLayout('list')}>
                    <List className="h-4 w-4 mr-2" /> List
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}
        </div>
      )}

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        Showing {filteredItems.length} of {items.length} items
        {selectedCategory !== 'all' && ` in "${selectedCategory}"`}
      </div>

      {/* Gallery Grid */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${layout}-${selectedCategory}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className={cn(
            layout === 'masonry' ? layoutConfigs[layout] : `grid gap-6 ${layoutConfigs[layout]}`,
            layout === 'masonry' && 'space-y-6'
          )}
        >
          {filteredItems.map((item, index) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={cn(
                "group relative",
                layout === 'masonry' && 'break-inside-avoid mb-6',
                layout === 'list' && 'flex gap-4 p-4 bg-card rounded-lg border'
              )}
            >
              {layout === 'list' ? (
                <>
                  {/* List Layout */}
                  <div className="w-48 h-32 flex-shrink-0">
                    <OptimizedImage
                      src={item.src}
                      alt={item.alt}
                      className="w-full h-full rounded-lg"
                      aspectRatio="3/2"
                      enableLightbox={enableLightbox}
                      lightboxTitle={item.title}
                      {...ImagePresets.thumbnail}
                    />
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="font-semibold text-lg">{item.title || item.alt}</h3>
                    {item.category && (
                      <span className="inline-block px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                        {item.category}
                      </span>
                    )}
                    {item.description && (
                      <p className="text-muted-foreground text-sm line-clamp-3">{item.description}</p>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* Grid/Masonry Layout */}
                  <div className="relative overflow-hidden rounded-lg">
                    <OptimizedImage
                      src={item.src}
                      alt={item.alt}
                      className="w-full h-full"
                      aspectRatio={layout === 'masonry' ? undefined : aspectRatio}
                      style={layout === 'masonry' ? { height: getItemHeight(index) } : undefined}
                      enableLightbox={enableLightbox}
                      lightboxTitle={item.title}
                      showDownload={true}
                      {...ImagePresets.gallery}
                    />
                    
                    {/* Featured badge */}
                    {item.featured && (
                      <div className="absolute top-3 left-3 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                        Featured
                      </div>
                    )}

                    {/* Overlay with info */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <div className="absolute bottom-4 left-4 right-4 text-white">
                        <h3 className="font-semibold text-lg mb-1">{item.title || item.alt}</h3>
                        {item.category && (
                          <span className="inline-block px-2 py-1 bg-white/20 backdrop-blur-sm text-xs rounded-full">
                            {item.category}
                          </span>
                        )}
                        {item.description && (
                          <p className="text-sm mt-2 line-clamp-2">{item.description}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>

      {/* Empty State */}
      {filteredItems.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Filter className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No items found</h3>
          <p className="text-muted-foreground">Try adjusting your filters or search criteria.</p>
          {selectedCategory !== 'all' && (
            <Button
              variant="outline"
              onClick={() => setSelectedCategory('all')}
              className="mt-4"
            >
              Show All Items
            </Button>
          )}
        </motion.div>
      )}
    </div>
  );
}
