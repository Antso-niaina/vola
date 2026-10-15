import { Link } from "react-router-dom";
import { ArrowDownLeft, Banknote, QrCode, ShoppingBag, Users } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/StatCard";
import { TransactionList } from "@/components/TransactionList";
import { useAuthStore } from "@/hooks/useAuthStore";
import { CommercantAPI, PortefeuilleAPI } from "@/services/api";
import { currency, mapMerchantPayment } from "@/lib/apiMappers";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const MerchantDashboard = () => {
  const { user } = useAuthStore();
  const { data: wallet } = useQuery({
    queryKey: ["wallet", user?.id_utilisateur],
    queryFn: PortefeuilleAPI.solde,
    enabled: Boolean(user),
    refetchInterval: 5000,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
  });
  const { data: revenues = [] } = useQuery({
    queryKey: ["merchant-revenues", user?.id_utilisateur],
    queryFn: CommercantAPI.historiqueRevenus,
    enabled: Boolean(user),
    refetchInterval: 5000,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
  });
  const { data: loyalClients = [] } = useQuery({ queryKey: ["merchant-loyal-clients"], queryFn: CommercantAPI.clientsFideles });

  const today = new Date().toISOString().slice(0, 10);
  const todaySales = revenues
    .filter((payment) => payment.date_paiement?.startsWith(today))
    .reduce((total, payment) => total + Number(payment.montant), 0);
  const recentSales = revenues.slice(0, 5).map(mapMerchantPayment);
  const chartData = revenues.slice(0, 7).reverse().map((payment) => ({
    day: new Date(payment.date_paiement).toLocaleDateString("fr-FR", { weekday: "short" }),
    sales: Number(payment.montant),
  }));
  const chartTotal = chartData.reduce((total, item) => total + item.sales, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Bonjour</p>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">{user?.nom_boutique || user?.username || "Boutique"}</h1>
        </div>
        <Button asChild className="bg-gradient-gold text-gold-foreground shadow-gold">
          <Link to="/commercant/qr">
            <QrCode className="h-4 w-4" />
            Afficher mon QR
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Solde" value={wallet ? currency(Number(wallet.solde)) : "Chargement..."} icon={Banknote} variant="primary" />
        <StatCard label="Ventes du jour" value={currency(todaySales)} icon={ShoppingBag} variant="gold" />
        <StatCard label="Transactions" value={revenues.length.toLocaleString("fr-FR")} icon={ArrowDownLeft} />
        <StatCard label="Clients fidèles" value={loyalClients.length.toLocaleString("fr-FR")} icon={Users} />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="font-display text-lg font-bold">Ventes des 7 derniers jours</h3>
              <p className="text-xs text-muted-foreground">Volume selon vos paiements reçus</p>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-3 py-1 text-xs font-semibold text-success">
              {currency(chartTotal)}
            </span>
          </div>
          <div className="h-64">
            {chartData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Aucune vente à afficher.</div>
            ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <defs>
                  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.95} />
                    <stop offset="100%" stopColor="hsl(var(--primary-glow))" stopOpacity={0.6} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px" }} />
                <Bar dataKey="sales" fill="url(#bar)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="space-y-4 rounded-2xl border border-border bg-card p-5 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Top clients</h3>
          {loyalClients.slice(0, 4).map((c, i) => (
            <div key={c.id_client} className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-primary text-sm font-bold text-primary-foreground">
                {i + 1}
              </div>
              <div className="flex-1">
                <p className="font-medium">Client #{c.id_client}</p>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-gradient-gold" style={{ width: `${Math.min(100, (Number(c.montant_total) / Number(loyalClients[0]?.montant_total || 1)) * 100)}%` }} />
                </div>
              </div>
              <span className="font-display text-sm font-bold text-primary">{currency(Number(c.montant_total))}</span>
            </div>
          ))}
          {loyalClients.length === 0 && <p className="text-sm text-muted-foreground">Aucun client fidèle pour l'instant.</p>}
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="font-display text-lg font-bold">Paiements récents</h3>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/commercant/ventes">Tout voir</Link>
          </Button>
        </div>
        <TransactionList transactions={recentSales} perspective="merchant" />
        {recentSales.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Aucune vente pour l'instant.</p>}
      </div>
    </div>
  );
};

export default MerchantDashboard;
