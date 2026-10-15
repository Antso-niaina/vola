import { Outlet } from "react-router-dom";
import { LayoutDashboard, CheckSquare, Users, ArrowLeftRight, BarChart3 } from "lucide-react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { useAuthStore } from "@/hooks/useAuthStore";
import { initials } from "@/lib/apiMappers";

const items = [
  { label: "Vue", to: "/admin", icon: LayoutDashboard, end: true },
  { label: "Validations", to: "/admin/validations", icon: CheckSquare },
  { label: "Utilisateurs", to: "/admin/utilisateurs", icon: Users },
  { label: "Transactions", to: "/admin/transactions", icon: ArrowLeftRight },
  { label: "Rapports", to: "/admin/rapports", icon: BarChart3 },
];

const AdminLayout = () => {
  const { user } = useAuthStore();
  const name = user?.username ?? "Admin";

  return (
    <DashboardLayout
      items={items}
      roleLabel="Administrateur"
      user={{ name, subtitle: "Administrateur MadaVola", initials: initials(name) }}
    >
      <Outlet />
    </DashboardLayout>
  );
};

export default AdminLayout;
