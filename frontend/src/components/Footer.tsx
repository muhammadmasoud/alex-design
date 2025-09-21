import { NavLink } from "react-router-dom";
import { Instagram, Facebook, Linkedin, Mail, Phone, MapPin } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import BehanceIcon from "@/components/icons/BehanceIcon";

export default function Footer() {
  const { isAdmin } = useAuth();

  return (
    <footer className="border-t bg-gradient-to-b from-background to-muted/30">
      <div className="container py-8 sm:py-10 md:py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <h3 className="font-heading text-lg">Alx Designs</h3>
            <p className="text-sm text-muted-foreground max-w-sm">Creative visuals, modern experiences, and pixel-perfect delivery. Let’s build something stunning.</p>
            <div className="flex gap-2 pt-1">
              <a href="https://www.instagram.com/alexandria.designs?igsh=MTJha3I5eHViYWZldA==" target="_blank" rel="noopener noreferrer" aria-label="Instagram" className="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background hover:bg-accent/60 transition-colors">
                <Instagram className="h-4 w-4" />
              </a>
              <a href="https://www.facebook.com/mohamed.a.aboelhamd" target="_blank" rel="noopener noreferrer" aria-label="Facebook" className="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background hover:bg-accent/60 transition-colors">
                <Facebook className="h-4 w-4" />
              </a>
              <a href="https://www.linkedin.com/in/muhammadaboelhamd" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" className="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background hover:bg-accent/60 transition-colors">
                <Linkedin className="h-4 w-4" />
              </a>
              <a href="https://www.behance.net/mohamedaboelhamd" target="_blank" rel="noopener noreferrer" aria-label="Behance" className="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background hover:bg-accent/60 transition-colors">
                <BehanceIcon className="h-6 w-6" />
              </a>
            </div>
          </div>

          <nav className="grid grid-cols-2 gap-2 text-sm">
            <NavLink to="/" end className="px-3 py-2 rounded-md hover:bg-accent/60">Home</NavLink>
            <NavLink to="/projects" className="px-3 py-2 rounded-md hover:bg-accent/60">Projects</NavLink>
            <NavLink to="/services" className="px-3 py-2 rounded-md hover:bg-accent/60">Services</NavLink>
            <NavLink to="/about" className="px-3 py-2 rounded-md hover:bg-accent/60">About</NavLink>
            <NavLink to="/contact" className="px-3 py-2 rounded-md hover:bg-accent/60">Contact</NavLink>
            {isAdmin && (
              <NavLink to="/admin-dashboard" className="px-3 py-2 rounded-md hover:bg-accent/60">Admin</NavLink>
            )}
          </nav>

          <div className="space-y-3">
            <h4 className="font-medium text-sm tracking-wide text-foreground/90">Contact</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="mailto:hello@alxdesigns.dev" className="group flex items-center gap-3 rounded-md px-3 py-2 hover:bg-accent/60 transition-colors">
                  <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border text-muted-foreground group-hover:text-foreground">
                    <Mail className="h-4 w-4" />
                  </span>
                  <span className="truncate">mohamedaboelhamd765@gmail.com</span>
                </a>
              </li>
              <li>
                <a href="tel:+201234567890" className="group flex items-center gap-3 rounded-md px-3 py-2 hover:bg-accent/60 transition-colors">
                  <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border text-muted-foreground group-hover:text-foreground">
                    <Phone className="h-4 w-4" />
                  </span>
                  <span className="truncate">+20 102 651 7446</span>
                </a>
              </li>
              <li>
                <div className="flex items-center gap-3 rounded-md px-3 py-2">
                  <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border text-muted-foreground">
                    <MapPin className="h-4 w-4" />
                  </span>
                  <span>Alexandria, Egypt</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t flex flex-col md:flex-row items-center justify-between gap-3">
          <p className="text-xs sm:text-sm text-muted-foreground text-center md:text-left">© {new Date().getFullYear()} Alx Designs. All rights reserved.</p>
          <div className="text-xs sm:text-sm text-muted-foreground">
            <span>Made with passion for performance.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
