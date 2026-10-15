import { Download, Search } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TransactionList } from "@/components/TransactionList";
import { TransactionAPI } from "@/services/api";
import { mapTransaction } from "@/lib/apiMappers";

const AdminTransactions = () => {
  const { data = [], isLoading } = useQuery({ queryKey: ["admin-top-transactions"], queryFn: () => TransactionAPI.topTransactions(50) });
  const all = data.map((tx) => mapTransaction(tx)).sort((a, b) => (a.date > b.date ? -1 : 1));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Toutes les transactions</h1>
          <p className="mt-1 text-sm text-muted-foreground">Supervision globale du réseau MadaVola.</p>
        </div>
        <Button variant="outline">
          <Download className="h-4 w-4" />
          Exporter
        </Button>
      </div>

      <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input className="pl-9" placeholder="Rechercher par ID, référence, utilisateur..." />
          </div>
          <select className="rounded-lg border border-input bg-background px-3 py-2 text-sm">
            <option>Tous les types</option>
            <option>Envoi</option>
            <option>Paiement</option>
            <option>Dépôt</option>
            <option>Retrait</option>
          </select>
          <select className="rounded-lg border border-input bg-background px-3 py-2 text-sm">
            <option>Tous statuts</option>
            <option>Validée</option>
            <option>En attente</option>
            <option>Rejetée</option>
          </select>
        </div>

        <div className="mt-4">
          {isLoading ? (
            <p className="py-8 text-center text-sm text-muted-foreground">Chargement...</p>
          ) : (
            <TransactionList transactions={all} />
          )}
          {!isLoading && all.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Aucune transaction.</p>}
        </div>
      </div>
    </div>
  );
};

export default AdminTransactions;
