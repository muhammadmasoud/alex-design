import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function PaginationControls({ page, totalPages, onPageChange }: Props) {
  if (totalPages <= 1) return null;

  // Show fewer pages on mobile, more on desktop
  const maxVisiblePages = window.innerWidth < 640 ? 3 : 7;
  
  // Calculate which pages to show
  let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
  
  // Adjust start page if we're near the end
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }
  
  const pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

  return (
    <Pagination>
      <PaginationContent className="gap-1">
        <PaginationItem>
          <PaginationPrevious 
            href="#" 
            onClick={(e) => { e.preventDefault(); if (page > 1) onPageChange(page - 1); }}
            className="h-9 w-9 sm:h-10 sm:w-auto"
          />
        </PaginationItem>
        
        {/* Show first page if not in range */}
        {startPage > 1 && (
          <>
            <PaginationItem>
              <PaginationLink 
                href="#" 
                onClick={(e) => { e.preventDefault(); onPageChange(1); }}
                className="h-9 w-9 text-sm"
              >
                1
              </PaginationLink>
            </PaginationItem>
            {startPage > 2 && (
              <PaginationItem>
                <span className="flex h-9 w-9 items-center justify-center text-sm">...</span>
              </PaginationItem>
            )}
          </>
        )}
        
        {pages.map((p) => (
          <PaginationItem key={p}>
            <PaginationLink 
              href="#" 
              isActive={p === page} 
              onClick={(e) => { e.preventDefault(); onPageChange(p); }}
              className="h-9 w-9 text-sm"
            >
              {p}
            </PaginationLink>
          </PaginationItem>
        ))}
        
        {/* Show last page if not in range */}
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && (
              <PaginationItem>
                <span className="flex h-9 w-9 items-center justify-center text-sm">...</span>
              </PaginationItem>
            )}
            <PaginationItem>
              <PaginationLink 
                href="#" 
                onClick={(e) => { e.preventDefault(); onPageChange(totalPages); }}
                className="h-9 w-9 text-sm"
              >
                {totalPages}
              </PaginationLink>
            </PaginationItem>
          </>
        )}
        
        <PaginationItem>
          <PaginationNext 
            href="#" 
            onClick={(e) => { e.preventDefault(); if (page < totalPages) onPageChange(page + 1); }}
            className="h-9 w-9 sm:h-10 sm:w-auto"
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
