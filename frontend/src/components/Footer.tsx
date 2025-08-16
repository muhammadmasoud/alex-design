export default function Footer() {
  return (
    <footer className="border-t">
      <div className="container py-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} Alx Designs. All rights reserved.</p>
          <nav className="flex gap-4 text-sm text-muted-foreground">
            <a href="#" className="story-link">Privacy</a>
            <a href="#" className="story-link">Terms</a>
            <a href="https://www.behance.net/mohamedaboelhamd" target="_blank" rel="noopener noreferrer" className="story-link">Behance</a>
          </nav>
        </div>
      </div>
    </footer>
  );
}
