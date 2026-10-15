import { Link } from "react-router-dom";
import { ArrowDownLeft, ArrowUpRight, Eye, EyeOff, PiggyBank, QrCode, Send, Banknote } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { TransactionList } from "@/components/TransactionList";
import { currency, mapTransaction } from "@/lib/apiMappers";
import { PortefeuilleAPI, TransactionAPI } from "@/services/api";
import { useAuthStore } from "@/hooks/useAuthStore";
import { useQuery } from "@tanstack/react-query";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const quickActions = [
  { icon: Send, label: "Envoyer", to: "/client/envoyer", color: "from-primary to-primary-glow" },
  { icon: QrCode, label: "Payer", to: "/client/payer", color: "from-gold to-gold-glow" },
  { icon: PiggyBank, label: "Déposer", to: "/client/cash?op=depot", color: "from-success to-primary-glow" },
  { icon: Banknote, label: "Retirer", to: "/client/cash?op=retrait", color: "from-warning to-gold" },
];

const toDayKey = (date: string) => new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });

const ClientDashboard = () => {
  const [show, setShow] = useState(true);
  const { user } = useAuthStore();
  const { data: wallet } = useQuery({
    queryKey: ["wallet", user?.id_utilisateur],
    queryFn: PortefeuilleAPI.solde,
    enabled: Boolean(user),
    refetchOnMount: "always",
  });
  const { data: apiTransactions = [] } = useQuery({
    queryKey: ["transactions", user?.id_utilisateur],
    queryFn: TransactionAPI.historique,
    enabled: Boolean(user),
  });
  const transactions = apiTransactions.map((tx) => mapTransaction(tx, user?.username));
  const balance = Number(wallet?.solde ?? 0);
  const incoming = transactions.filter((tx) => tx.type === "reception" || tx.type === "depot").reduce((total, tx) => total + tx.amount, 0);
  const outgoing = transactions.filter((tx) => tx.type === "envoi" || tx.type === "paiement" || tx.type === "retrait").reduce((total, tx) => total + tx.amount, 0);
  const activityData = transactions.reduce<Array<{ day: string; in: number; out: number }>>((days, tx) => {
    const day = toDayKey(tx.date);
    const current = days.find((item) => item.day === day);
    const row = current ?? { day, in: 0, out: 0 };
    if (!current) days.push(row);
    if (tx.type === "reception" || tx.type === "depot") row.in += tx.amount;
    if (tx.type === "envoi" || tx.type === "paiement" || tx.type === "retrait") row.out += tx.amount;
    return days;
  }, []).slice(0, 7).reverse();
  const securityRows = [
    { l: "Statut du compte", v: user?.statut_compte ?? "—" },
    { l: "Rôle", v: user?.role ?? "—" },
    { l: "Téléphone", v: user?.telephone || wallet?.telephone || "—" },
    { l: "Transactions visibles", v: transactions.length.toLocaleString("fr-FR") },
  ];

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">Bonjour</p>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">{user?.username}, bienvenue sur votre portefeuille</h1>
      </div>

      
      <div className="relative overflow-hidden rounded-3xl bg-gradient-card p-6 text-primary-foreground shadow-elegant md:p-8">
        <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-gold/20 blur-3xl" />
        <div className="absolute -bottom-20 left-10 h-48 w-48 rounded-full bg-primary-glow/40 blur-3xl" />
        <div className="relative z-10 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest opacity-70">Solde disponible</p>
            <div className="mt-2 flex items-center gap-3">
              <p className="font-display text-4xl font-extrabold md:text-5xl">
                {show ? currency(balance) : "•••••• Ar"}
              </p>
              <button
                onClick={() => setShow(!show)}
                className="rounded-full bg-primary-foreground/10 p-2 transition-smooth hover:bg-primary-foreground/20"
                aria-label="Basculer la visibilité du solde"
              >
                {show ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </button>
            </div>
            <p className="mt-2 text-sm opacity-70">
              Téléphone : <span className="font-mono">{wallet?.telephone ?? user?.telephone}</span>
            </p>
          </div>
          <div className="rounded-2xl bg-primary-foreground/10 p-3 backdrop-blur">
            <p className="text-[10px] uppercase tracking-widest opacity-70">Ce mois</p>
            <p className="mt-1 flex items-center gap-1 font-display text-lg font-bold text-gold">
              <ArrowDownLeft className="h-4 w-4" /> +{currency(incoming)}
            </p>
            <p className="flex items-center gap-1 text-sm opacity-90">
              <ArrowUpRight className="h-4 w-4" /> -{currency(outgoing)}
            </p>
          </div>
        </div>

        <div className="relative z-10 mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          {quickActions.map((a) => (
            <Link
              key={a.label}
              to={a.to}
              className="group flex flex-col items-center gap-2 rounded-2xl bg-primary-foreground/10 p-4 backdrop-blur transition-smooth hover:bg-primary-foreground/20"
            >
              <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${a.color} shadow-glow`}>
                <a.icon className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-sm font-semibold">{a.label}</span>
            </Link>
          ))}
        </div>
      </div>

      
      <div className="grid gap-5 lg:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="font-display text-lg font-bold">Activité de la semaine</h3>
              <p className="text-xs text-muted-foreground">Entrées et sorties selon votre historique</p>
            </div>
          </div>
          <div className="h-64">
            {activityData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Aucune activité à afficher.</div>
            ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="in" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--success))" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="hsl(var(--success))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="out" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--gold))" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="hsl(var(--gold))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "12px",
                  }}
                />
                <Area type="monotone" dataKey="in" stroke="hsl(var(--success))" strokeWidth={2} fill="url(#in)" />
                <Area type="monotone" dataKey="out" stroke="hsl(var(--gold))" strokeWidth={2} fill="url(#out)" />
              </AreaChart>
            </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Compte</h3>
          <p className="mt-1 text-xs text-muted-foreground">Données renvoyées par votre profil backend.</p>
          <div className="mt-4 space-y-3">
            {securityRows.map((s) => (
              <div key={s.l} className="flex items-center justify-between rounded-xl bg-muted/40 px-3 py-2.5">
                <span className="text-sm">{s.l}</span>
                <span className="text-right text-xs font-semibold text-success">{s.v}</span>
              </div>
            ))}
          </div>
          <Button variant="outline" className="mt-4 w-full" asChild>
            <Link to="/client/historique">Voir tout l'historique</Link>
          </Button>
        </div>
      </div>

      
      <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="font-display text-lg font-bold">Dernières transactions</h3>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/client/historique">Tout voir</Link>
          </Button>
        </div>
        <TransactionList transactions={transactions.slice(0, 5)} />
      </div>
    </div>
  );
};

export default ClientDashboard;
