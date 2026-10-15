import { useState } from "react";
import { Check, Clock, PiggyBank, Banknote, X } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { currency, mapPendingRequest } from "@/lib/apiMappers";
import { formatApiError, TransactionAPI } from "@/services/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const AdminValidations = () => {
  const [filter, setFilter] = useState<"all" | "depot" | "retrait">("all");
  const queryClient = useQueryClient();
  const { data: deposits = [], isLoading: loadingDeposits } = useQuery({ queryKey: ["pending-deposits"], queryFn: TransactionAPI.depotsEnAttente });
  const { data: withdrawals = [], isLoading: loadingWithdrawals } = useQuery({ queryKey: ["pending-withdrawals"], queryFn: TransactionAPI.retraitsEnAttente });
  const requests = [
    ...deposits.map((item) => mapPendingRequest(item, "depot")),
    ...withdrawals.map((item) => mapPendingRequest(item, "retrait")),
  ];

  const filtered = requests.filter((r) => filter === "all" || r.type === filter);

  const action = async (request: (typeof requests)[number], ok: boolean) => {
    try {
      const response = request.type === "depot"
        ? ok ? await TransactionAPI.validerDepot(request.id) : await TransactionAPI.refuserDepot(request.id)
        : ok ? await TransactionAPI.validerRetrait(request.id) : await TransactionAPI.refuserRetrait(request.id);
      toast.success(ok ? "Demande validée" : "Demande rejetée", { description: response.detail });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["pending-deposits"] }),
        queryClient.invalidateQueries({ queryKey: ["pending-withdrawals"] }),
      ]);
    } catch (error) {
      toast.error("Action impossible", { description: formatApiError(error) });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Validations</h1>
        <p className="mt-1 text-sm text-muted-foreground">Approuvez les dépôts et retraits soumis par les utilisateurs.</p>
      </div>

      <div className="flex gap-2">
        {(["all", "depot", "retrait"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-full px-4 py-1.5 text-xs font-semibold transition-smooth",
              filter === f ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/70"
            )}
          >
            {f === "all" ? "Toutes" : f === "depot" ? "Dépôts" : "Retraits"}
          </button>
        ))}
      </div>

      <div className="rounded-2xl border border-border bg-card shadow-card-soft">
        <div className="hidden grid-cols-12 gap-4 border-b border-border px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground md:grid">
          <div className="col-span-1">Type</div>
          <div className="col-span-3">Utilisateur</div>
          <div className="col-span-2">Référence</div>
          <div className="col-span-2">Date</div>
          <div className="col-span-2 text-right">Montant</div>
          <div className="col-span-2 text-right">Action</div>
        </div>

        <div className="divide-y divide-border">
          {loadingDeposits || loadingWithdrawals ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Chargement...</p>
          ) : filtered.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Aucune demande en attente.</p>
          ) : (
            filtered.map((r) => (
              <div key={r.ref} className="grid grid-cols-12 items-center gap-4 px-5 py-4">
                <div className="col-span-12 md:col-span-1">
                  <div
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-xl",
                      r.type === "depot" ? "bg-success/10 text-success" : "bg-warning/10 text-warning"
                    )}
                  >
                    {r.type === "depot" ? <PiggyBank className="h-5 w-5" /> : <Banknote className="h-5 w-5" />}
                  </div>
                </div>
                <div className="col-span-6 md:col-span-3">
                  <p className="font-semibold">{r.user}</p>
                  <p className="text-xs text-muted-foreground">{r.phone}</p>
                </div>
                <div className="col-span-6 md:col-span-2">
                  <p className="font-mono text-xs">{r.ref}</p>
                </div>
                <div className="col-span-6 md:col-span-2">
                  <p className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {r.date}
                  </p>
                </div>
                <div className="col-span-6 md:col-span-2 md:text-right">
                  <p className="font-display text-base font-bold text-primary">{currency(r.amount)}</p>
                </div>
                <div className="col-span-12 flex gap-2 md:col-span-2 md:justify-end">
                  <Button size="sm" variant="outline" onClick={() => action(r, false)}>
                    <X className="h-4 w-4" /> Rejeter
                  </Button>
                  <Button size="sm" onClick={() => action(r, true)} className="bg-gradient-primary">
                    <Check className="h-4 w-4" /> Valider
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminValidations;
