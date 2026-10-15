import { Download, FileBarChart, FileText, ShieldAlert } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/StatCard";
import { currency } from "@/lib/apiMappers";
import { StatsAPI } from "@/services/api";
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const pieData = [
  { name: "Paiements commerçants", value: 48 },
  { name: "Transferts P2P", value: 27 },
  { name: "Dépôts", value: 15 },
  { name: "Retraits", value: 10 },
];

const COLORS = ["hsl(var(--primary))", "hsl(var(--gold))", "hsl(var(--success))", "hsl(var(--warning))"];

const AdminReports = () => {
  const { data: txStats } = useQuery({ queryKey: ["reports-tx-stats"], queryFn: StatsAPI.nbrTransactions });
  const { data: periodStats = [] } = useQuery({ queryKey: ["reports-period"], queryFn: () => StatsAPI.transactionsParPeriode("jour") });
  const { data: topMerchants = [] } = useQuery({ queryKey: ["reports-top-merchants"], queryFn: () => StatsAPI.topCommercants(5) });
  const volumeChartData = periodStats.map((item, index) => ({
    day: String(item.periode ?? item.date ?? index + 1),
    volume: Number(item.volume ?? item.montant_total ?? item.total_montant ?? 0),
    transactions: Number(item.nombre ?? item.total ?? item.nb_transactions ?? 0),
  }));
  const totalVolume = volumeChartData.reduce((total, item) => total + item.volume, 0);
  const totalTransactions = typeof txStats === "number" ? txStats : Number(txStats?.nombre_transactions ?? txStats?.total ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Rapports & Analytics</h1>
          <p className="mt-1 text-sm text-muted-foreground">Statistiques globales et exports comptables.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="h-4 w-4" />
            Rapport mensuel
          </Button>
          <Button className="bg-gradient-primary">
            <Download className="h-4 w-4" />
            Exporter PDF
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Volume total" value={currency(totalVolume)} icon={FileBarChart} variant="primary" />
        <StatCard label="Transactions" value={totalTransactions.toLocaleString("fr-FR")} icon={FileBarChart} variant="gold" />
        <StatCard label="Périodes suivies" value={volumeChartData.length.toLocaleString("fr-FR")} icon={FileBarChart} />
        <StatCard label="Alertes fraude" value="—" icon={ShieldAlert} />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft lg:col-span-2">
          <h3 className="font-display text-lg font-bold">Évolution hebdomadaire</h3>
          <p className="text-xs text-muted-foreground">Volume vs nombre de transactions</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={volumeChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px" }} />
                <Legend />
                <Line type="monotone" dataKey="volume" stroke="hsl(var(--primary))" strokeWidth={3} dot={{ r: 4 }} name="Volume (M Ar)" />
                <Line type="monotone" dataKey="transactions" stroke="hsl(var(--gold))" strokeWidth={3} dot={{ r: 4 }} name="Nb transactions" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Répartition des flux</h3>
          <p className="text-xs text-muted-foreground">Par type de transaction</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={4}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            {pieData.map((p, i) => (
              <div key={p.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: COLORS[i] }} />
                  <span>{p.name}</span>
                </div>
                <span className="font-semibold">{p.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-gradient-hero p-6 text-primary-foreground shadow-elegant">
        <h3 className="font-display text-xl font-bold">Top 5 commerçants (Algorithme Top-K)</h3>
        <p className="mt-1 text-sm opacity-80">Les plus actifs cette semaine</p>
        <div className="mt-5 space-y-3">
          {topMerchants.map((m, i) => {
            const amount = Number(m.montant_total ?? m.total ?? 0);
            const max = Number(topMerchants[0]?.montant_total ?? topMerchants[0]?.total ?? 1);
            const name = m.nom_boutique ?? m.commercant ?? `Commerçant #${i + 1}`;
            return (
            <div key={name} className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gold font-bold text-gold-foreground">
                {i + 1}
              </div>
              <p className="flex-1 font-semibold">{name}</p>
              <div className="h-2 w-32 overflow-hidden rounded-full bg-primary-foreground/20">
                <div className="h-full bg-gradient-gold" style={{ width: `${Math.min(100, (amount / max) * 100)}%` }} />
              </div>
              <p className="w-32 text-right font-display text-sm font-bold text-gold">{currency(amount)}</p>
            </div>
          )})}
          {topMerchants.length === 0 && <p className="text-sm opacity-80">Aucune donnée disponible.</p>}
        </div>
      </div>
    </div>
  );
};

export default AdminReports;
