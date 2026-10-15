import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, Clock, ShieldCheck, Store, TrendingUp, Users, Wallet } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { StatCard } from "@/components/StatCard";
import { Button } from "@/components/ui/button";
import { currency, mapPendingRequest } from "@/lib/apiMappers";
import { AuthAPI, StatsAPI } from "@/services/api";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const numberFrom = (value: unknown, keys: string[]) => {
  if (typeof value === "number") return value;
  if (value && typeof value === "object") {
    const data = value as Record<string, unknown>;
    const match = keys.find((key) => data[key] !== undefined);
    return Number(match ? data[match] : 0);
  }
  return 0;
};

const AdminDashboard = () => {
  const { data: usersStats } = useQuery({ queryKey: ["admin-users-stats"], queryFn: StatsAPI.nbrUtilisateurs });
  const { data: users = [] } = useQuery({ queryKey: ["admin-users"], queryFn: AuthAPI.listeUtilisateurs });
  const { data: txStats } = useQuery({ queryKey: ["admin-tx-stats"], queryFn: StatsAPI.nbrTransactions });
  const { data: deposits = [] } = useQuery({ queryKey: ["stats-pending-deposits"], queryFn: StatsAPI.depotsAttente });
  const { data: withdrawals = [] } = useQuery({ queryKey: ["stats-pending-withdrawals"], queryFn: StatsAPI.retraitsAttente });
  const { data: periodStats = [] } = useQuery({ queryKey: ["admin-period-stats"], queryFn: () => StatsAPI.transactionsParPeriode("jour") });
  const { data: suspicious } = useQuery({ queryKey: ["admin-suspicious-transactions"], queryFn: () => StatsAPI.transactionsSuspectes() });
  const { data: metrics } = useQuery({ queryKey: ["admin-dashboard-metrics"], queryFn: () => StatsAPI.metriquesDashboard(15) });
  const pendingRequests = [
    ...deposits.map((item) => mapPendingRequest(item, "depot")),
    ...withdrawals.map((item) => mapPendingRequest(item, "retrait")),
  ];
  const chartData = periodStats.length
    ? periodStats.map((item, index) => ({
        day: String(item.periode ?? item.date ?? index + 1),
        volume: Number(item.volume_total ?? item.volume ?? item.montant_total ?? item.total_montant ?? 0),
        transactions: Number(item.nombre_transactions ?? item.nombre ?? item.total ?? item.nb_transactions ?? 0),
      }))
    : [];
  const userCount = users.length || numberFrom(usersStats, ["total_utilisateurs", "nombre_utilisateurs", "total"]);
  const merchantCount = users.filter((user) => user.role === "commercant").length || numberFrom(usersStats, ["total_commercants"]);
  const transactionCount = numberFrom(txStats, ["total_transactions", "nombre_transactions", "total"]);
  const totalVolume = numberFrom(txStats, ["volume_total"]) || chartData.reduce((total, item) => total + item.volume, 0);
  const suspiciousCount = numberFrom(suspicious, ["nb_suspectes"]);
  const metricCount = Array.isArray((metrics as Record<string, unknown> | undefined)?.metriques_selectionnees)
    ? ((metrics as { metriques_selectionnees: unknown[] }).metriques_selectionnees.length)
    : 0;
  const systemRows = [
    { l: "Dépôts en attente", v: deposits.length.toLocaleString("fr-FR") },
    { l: "Retraits en attente", v: withdrawals.length.toLocaleString("fr-FR") },
    { l: "Transactions suspectes", v: suspiciousCount.toLocaleString("fr-FR") },
    { l: "Métriques actives", v: metricCount.toLocaleString("fr-FR") },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Console d'administration</p>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Vue d'ensemble MadaVola</h1>
        </div>
        <Button asChild className="bg-gradient-primary">
          <Link to="/admin/validations">
            <CheckCircle2 className="h-4 w-4" />
            {pendingRequests.length} demandes en attente
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Utilisateurs" value={userCount.toLocaleString("fr-FR")} icon={Users} variant="primary" />
        <StatCard label="Commerçants" value={merchantCount.toLocaleString("fr-FR")} icon={Store} variant="gold" />
        <StatCard label="Volume traité" value={currency(totalVolume)} icon={Wallet} />
        <StatCard label="Transactions" value={transactionCount.toLocaleString("fr-FR")} icon={TrendingUp} />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="font-display text-lg font-bold">Volume des transactions (7 jours)</h3>
              <p className="text-xs text-muted-foreground">En millions d'Ariary</p>
            </div>
          </div>
          <div className="h-72">
            {chartData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Aucune donnée de période.</div>
            ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="vol" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px" }} />
                <Area type="monotone" dataKey="volume" stroke="hsl(var(--primary))" strokeWidth={2.5} fill="url(#vol)" />
              </AreaChart>
            </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Transactions / jour</h3>
          <p className="text-xs text-muted-foreground">Algorithme Top-K en action</p>
          <div className="mt-4 h-64">
            {chartData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Aucune transaction à afficher.</div>
            ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px" }} />
                <Bar dataKey="transactions" fill="hsl(var(--gold))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-display text-lg font-bold">Demandes en attente</h3>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/admin/validations">
                Tout voir <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
          <div className="space-y-2">
            {pendingRequests.slice(0, 4).map((r) => (
              <div key={r.ref} className="flex items-center gap-3 rounded-xl bg-muted/40 p-3">
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                    r.type === "depot" ? "bg-success/10 text-success" : "bg-warning/10 text-warning"
                  }`}
                >
                  {r.type === "depot" ? <Wallet className="h-4 w-4" /> : <Clock className="h-4 w-4" />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold">{r.user}</p>
                  <p className="text-xs text-muted-foreground">
                    {r.ref} · {r.date}
                  </p>
                </div>
                <p className="font-display text-sm font-bold text-primary">{currency(r.amount)}</p>
              </div>
            ))}
            {pendingRequests.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Aucune demande en attente.</p>}
          </div>
        </div>

        <div className="rounded-2xl bg-gradient-hero p-6 text-primary-foreground shadow-elegant">
          <ShieldCheck className="h-8 w-8 text-gold" />
          <h3 className="mt-3 font-display text-xl font-bold">État opérationnel</h3>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {systemRows.map((s) => (
              <div key={s.l} className="rounded-xl bg-primary-foreground/10 p-3 backdrop-blur">
                <p className="text-[10px] uppercase tracking-widest opacity-70">{s.l}</p>
                <p className="mt-1 font-display text-xl font-bold text-gold">{s.v}</p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm opacity-80">
            Ces indicateurs viennent des endpoints de statistiques et des files de validation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
