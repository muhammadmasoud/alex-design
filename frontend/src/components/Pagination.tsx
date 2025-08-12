import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function PaginationControls({ page, totalPages, onPageChange }: Props) {
  if (totalPages <= 1) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1).slice(0, 10);

  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious href="#" onClick={(e) => { e.preventDefault(); if (page > 1) onPageChange(page - 1); }} />
        </PaginationItem>
        {pages.map((p) => (
          <PaginationItem key={p}>
            <PaginationLink href="#" isActive={p === page} onClick={(e) => { e.preventDefault(); onPageChange(p); }}>
              {p}
            </PaginationLink>
          </PaginationItem>
        ))}
        <PaginationItem>
          <PaginationNext href="#" onClick={(e) => { e.preventDefault(); if (page < totalPages) onPageChange(page + 1); }} />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
