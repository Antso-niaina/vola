import { Outlet } from "react-router-dom";
import { LayoutDashboard, Send, QrCode, History, Wallet } from "lucide-react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { useAuthStore } from "@/hooks/useAuthStore";
import { initials } from "@/lib/apiMappers";

const items = [
  { label: "Accueil", to: "/client", icon: LayoutDashboard, end: true },
  { label: "Envoyer", to: "/client/envoyer", icon: Send },
  { label: "Payer QR", to: "/client/payer", icon: QrCode },
  { label: "Cash", to: "/client/cash", icon: Wallet },
  { label: "Historique", to: "/client/historique", icon: History },
];

const ClientLayout = () => {
  const { user } = useAuthStore();
  const name = user?.username ?? "Client";

  return (
    <DashboardLayout
      items={items}
      roleLabel="Client"
      user={{ name, subtitle: user?.telephone ?? "Portefeuille MadaVola", initials: initials(name) }}
    >
      <Outlet />
    </DashboardLayout>
  );
};

export default ClientLayout;
