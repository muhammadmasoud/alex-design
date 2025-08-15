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
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-heading text-xl">
          <img 
            src={logoImage} 
            alt="Alex Design Logo" 
            className="h-12 w-12 object-contain brightness-0 dark:invert"
          />
          <span>Alex Design</span>
        </Link>
        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/" className={linkClass} end>Home</NavLink>
          <NavLink to="/projects" className={linkClass}>Projects</NavLink>
          <NavLink to="/services" className={linkClass}>Services</NavLink>
          <NavLink to="/contact" className={linkClass}>Contact</NavLink>
          {isAdmin && (
            <NavLink to="/admin-dashboard" className={linkClass}>Admin</NavLink>
          )}
        </nav>
        <div className="flex items-center gap-2">
          {/* Mobile menu trigger */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72 sm:w-80">
              <SheetHeader>
                <SheetTitle className="flex items-center gap-2">
                  <img 
                    src={logoImage} 
                    alt="Alex Design Logo" 
                    className="h-10 w-10 object-contain brightness-0 dark:invert"
                  />
                  Alex Design
                </SheetTitle>
              </SheetHeader>
              <nav className="mt-6 grid gap-2">
                <SheetClose asChild><NavLink to="/" className={linkClass} end>Home</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/projects" className={linkClass}>Projects</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/services" className={linkClass}>Services</NavLink></SheetClose>
                <SheetClose asChild><NavLink to="/contact" className={linkClass}>Contact</NavLink></SheetClose>
                {isAdmin && (
                  <SheetClose asChild><NavLink to="/admin-dashboard" className={linkClass}>Admin</NavLink></SheetClose>
                )}
              </nav>
              <div className="mt-6">
                {!isAuthenticated ? (
                  <div className="grid gap-2">
                    <SheetClose asChild><Button variant="outline" asChild><Link to="/login">Log in</Link></Button></SheetClose>
                    <SheetClose asChild><Button asChild><Link to="/register">Sign up</Link></Button></SheetClose>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 px-2 py-1 text-sm">
                      <User className="h-4 w-4" />
                      <span>Welcome, {user?.username}</span>
                    </div>
                    <SheetClose asChild><Button variant="secondary" onClick={handleLogout} className="w-full">Logout</Button></SheetClose>
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>

          {/* Desktop auth section */}
          {!isAuthenticated ? (
            <div className="hidden sm:flex gap-2">
              <Button variant="ghost" asChild><Link to="/login">Log in</Link></Button>
              <Button asChild><Link to="/register">Sign up</Link></Button>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm">
                <User className="h-4 w-4" />
                <span>Welcome, {user?.username}</span>
              </div>
              <Button variant="secondary" onClick={handleLogout}>Logout</Button>
            </div>
          )}

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
