import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { LogOut, LucideIcon } from "lucide-react";
import { Logo } from "./Logo";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/hooks/useAuthStore";

export interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
  end?: boolean;
}

interface DashboardLayoutProps {
  items: NavItem[];
  roleLabel: string;
  user: { name: string; subtitle: string; initials: string };
  children: React.ReactNode;
  accentClass?: string;
}

export const DashboardLayout = ({ items, roleLabel, user, children }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const active = items.find((i) => (i.end ? location.pathname === i.to : location.pathname.startsWith(i.to)));

  const handleLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  return (
    <div className="min-h-screen bg-gradient-surface">
      <div className="flex min-h-screen w-full">
        
        <aside className="hidden w-72 flex-col bg-sidebar text-sidebar-foreground lg:flex">
          <div className="flex h-20 items-center border-b border-sidebar-border px-6">
            <Logo variant="light" />
          </div>

          <div className="px-6 py-5">
            <div className="rounded-xl bg-sidebar-accent/40 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/60">
                Espace
              </p>
              <p className="mt-0.5 font-display text-lg font-bold text-gold">{roleLabel}</p>
            </div>
          </div>

          <nav className="flex-1 space-y-1 px-4">
            {items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    cn(
                      "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-smooth",
                      isActive
                        ? "bg-gradient-to-r from-sidebar-accent to-sidebar-accent/40 text-sidebar-primary-foreground shadow-card-soft"
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent/40 hover:text-sidebar-foreground"
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span
                        className={cn(
                          "flex h-9 w-9 items-center justify-center rounded-lg transition-smooth",
                          isActive ? "bg-gold text-gold-foreground" : "bg-sidebar-accent/40 text-sidebar-foreground/70"
                        )}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <span>{item.label}</span>
                    </>
                  )}
                </NavLink>
              );
            })}
          </nav>

          <div className="space-y-3 border-t border-sidebar-border p-4">
            <div className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-sidebar-foreground/80">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-gold font-semibold text-gold-foreground">
                {user.initials}
              </div>
              <div className="flex-1 leading-tight">
                <p className="font-medium text-sidebar-foreground">{user.name}</p>
                <p className="text-xs text-sidebar-foreground/60">{user.subtitle}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start text-sidebar-foreground/80 hover:bg-sidebar-accent/40 hover:text-sidebar-foreground"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4" />
              Déconnexion
            </Button>
          </div>
        </aside>

        
        <main className="flex-1 overflow-x-hidden">
          
          <div className="flex items-center justify-between border-b border-border bg-card px-4 py-4 lg:hidden">
            <Logo />
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                {roleLabel}
              </span>
              <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Déconnexion">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>

          
          <nav className="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-5 border-t border-border bg-card/95 backdrop-blur lg:hidden">
            {items.slice(0, 5).map((item) => {
              const Icon = item.icon;
              const isActive = active?.to === item.to;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={cn(
                    "flex flex-col items-center justify-center gap-1 py-2.5 text-[10px] font-medium transition-smooth",
                    isActive ? "text-primary" : "text-muted-foreground"
                  )}
                >
                  <Icon className={cn("h-5 w-5", isActive && "scale-110")} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          <div className="px-4 pb-24 pt-6 sm:px-6 lg:px-10 lg:pb-10 lg:pt-8">{children}</div>
        </main>
      </div>
    </div>
  );
};
