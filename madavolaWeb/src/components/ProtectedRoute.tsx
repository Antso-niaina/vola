import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Role } from "@/services/api";
import { useAuthStore } from "@/hooks/useAuthStore";

export const homeForRole = (role: Role) => {
  if (role === "admin") return "/admin";
  if (role === "commercant") return "/commercant";
  return "/client";
};

export const ProtectedRoute = ({ roles }: { roles: Role[] }) => {
  const { user, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) return <div className="p-6 text-sm text-muted-foreground">Chargement...</div>;
  if (!user) return <Navigate to="/" replace state={{ from: location }} />;
  if (!roles.includes(user.role)) return <Navigate to={homeForRole(user.role)} replace />;

  return <Outlet />;
};
