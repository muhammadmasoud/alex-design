import { Link, NavLink, useNavigate } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetClose } from "@/components/ui/sheet";
import { Menu, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import logoImage from "@/assets/images/logo.png";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated, isAdmin } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium ${isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/60"}`;

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 sm:h-16 items-center justify-between px-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2 font-heading text-base sm:text-lg md:text-xl">
          <img 
            src={logoImage} 
            alt="Alex Design Logo" 
            className="h-8 w-8 sm:h-10 sm:w-10 md:h-12 md:w-12 object-contain brightness-0 dark:invert"
          />
          <span className="hidden sm:inline">Alx Designs</span>
        </Link>
        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/" className={linkClass} end>Home</NavLink>
          <NavLink to="/projects" className={linkClass}>Projects</NavLink>
          <NavLink to="/services" className={linkClass}>Services</NavLink>
          <NavLink to="/about" className={linkClass}>About</NavLink>
          <NavLink to="/contact" className={linkClass}>Contact</NavLink>
          {isAdmin && (
            <NavLink to="/admin-dashboard" className={linkClass}>Admin</NavLink>
          )}
        </nav>
        <div className="flex items-center gap-1">
          {/* Mobile menu trigger */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden h-9 w-9" aria-label="Open menu">
                <Menu className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-80 sm:w-96 p-6">
              <SheetHeader>
                <SheetTitle className="flex items-center gap-2">
                  <img 
                    src={logoImage} 
                    alt="Alex Design Logo" 
                    className="h-10 w-10 object-contain brightness-0 dark:invert"
                  />
                  Alx Design
                </SheetTitle>
              </SheetHeader>
              <nav className="mt-8 grid gap-3">
                <SheetClose asChild><NavLink to="/" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors" end>Home</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/projects" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors">Projects</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/services" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors">Services</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/about" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors">About</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/contact" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors">Contact</NavLink></SheetClose>
                {isAdmin && (
                  <SheetClose asChild><NavLink to="/admin-dashboard" className="block px-4 py-3 rounded-lg text-base font-medium hover:bg-accent/60 transition-colors">Admin</NavLink></SheetClose>
                )}
              </nav>
              <div className="mt-8 pt-6 border-t border-border">
                {!isAuthenticated ? (
                  <div className="grid gap-3">
                    <SheetClose asChild><Button variant="outline" size="lg" className="w-full" asChild><Link to="/login">Log in</Link></Button></SheetClose>
                    <SheetClose asChild><Button size="lg" className="w-full" asChild><Link to="/register">Sign up</Link></Button></SheetClose>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 px-4 py-3 bg-muted/50 rounded-lg text-sm">
                      <User className="h-5 w-5" />
                      <span>Welcome, {user?.username}</span>
                    </div>
                    <SheetClose asChild><Button variant="secondary" size="lg" onClick={handleLogout} className="w-full">Logout</Button></SheetClose>
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>

          {/* Desktop auth section */}
          {!isAuthenticated ? (
            <div className="hidden sm:flex gap-1 md:gap-2">
              <Button variant="ghost" size="sm" asChild><Link to="/login">Log in</Link></Button>
              <Button size="sm" asChild><Link to="/register">Sign up</Link></Button>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-2 md:gap-3">
              <div className="flex items-center gap-2 text-xs md:text-sm">
                <User className="h-3 w-3 md:h-4 md:w-4" />
                <span className="hidden md:inline">Welcome, {user?.username}</span>
                <span className="md:hidden">{user?.username}</span>
              </div>
              <Button variant="secondary" size="sm" onClick={handleLogout}>Logout</Button>
            </div>
          )}

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
