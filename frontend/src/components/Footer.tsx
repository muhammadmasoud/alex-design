export default function Footer() {
  return (
    <footer className="border-t">
      <div className="container py-6 sm:py-8 md:py-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-3 sm:gap-4">
          <p className="text-xs sm:text-sm text-muted-foreground text-center md:text-left">© {new Date().getFullYear()} Alx Designs. All rights reserved.</p>
          <nav className="flex gap-3 sm:gap-4 text-xs sm:text-sm text-muted-foreground">
            <a href="#" className="story-link">Privacy</a>
            <a href="#" className="story-link">Terms</a>
            <a href="https://www.behance.net/mohamedaboelhamd" target="_blank" rel="noopener noreferrer" className="story-link">Behance</a>
          </nav>
        </div>
      </div>
    </footer>
  );
}
