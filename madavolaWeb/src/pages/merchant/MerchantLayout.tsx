import { Outlet } from "react-router-dom";
import { LayoutDashboard, QrCode, ListOrdered, Banknote, Settings } from "lucide-react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { useAuthStore } from "@/hooks/useAuthStore";
import { initials } from "@/lib/apiMappers";

const items = [
  { label: "Accueil", to: "/commercant", icon: LayoutDashboard, end: true },
  { label: "Mon QR", to: "/commercant/qr", icon: QrCode },
  { label: "Ventes", to: "/commercant/ventes", icon: ListOrdered },
  { label: "Retrait", to: "/commercant/retrait", icon: Banknote },
  { label: "Profil", to: "/commercant/profil", icon: Settings },
];

const MerchantLayout = () => {
  const { user } = useAuthStore();
  const name = user?.nom_boutique ?? user?.username ?? "Commerçant";

  return (
    <DashboardLayout
      items={items}
      roleLabel="Commerçant"
      user={{ name, subtitle: user?.telephone ?? "Portefeuille MadaVola", initials: initials(name) }}
    >
      <Outlet />
    </DashboardLayout>
  );
};

export default MerchantLayout;
