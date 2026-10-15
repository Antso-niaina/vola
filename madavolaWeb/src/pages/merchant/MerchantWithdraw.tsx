import { useState } from "react";
import { Banknote, Building2, Clock } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { currency } from "@/lib/apiMappers";
import { formatApiError, PortefeuilleAPI, TransactionAPI } from "@/services/api";
import { toast } from "sonner";
import { useAuthStore } from "@/hooks/useAuthStore";

const MerchantWithdraw = () => {
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const { user } = useAuthStore();
  const { data: wallet } = useQuery({
    queryKey: ["wallet", user?.id_utilisateur],
    queryFn: PortefeuilleAPI.solde,
    enabled: Boolean(user),
    refetchInterval: 5000,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
  });
  const { data: withdrawals = [] } = useQuery({ queryKey: ["merchant-withdrawals"], queryFn: TransactionAPI.historique });

  const submit = async () => {
    if (!amount || Number(amount) <= 0) {
      toast.error("Montant invalide", { description: "Le montant doit être supérieur à 0." });
      return;
    }

    setLoading(true);
    try {
      const response = await TransactionAPI.demandeRetrait(Number(amount));
      toast.success("Demande envoyée", { description: response.detail });
      setAmount("");
    } catch (error) {
      toast.error("Demande impossible", { description: formatApiError(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Demander un retrait</h1>
        <p className="mt-1 text-sm text-muted-foreground">Convertissez votre solde MadaVola en argent physique.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-card-soft lg:col-span-2">
          <div className="rounded-2xl bg-gradient-card p-5 text-primary-foreground">
            <p className="text-xs font-semibold uppercase tracking-widest opacity-70">Solde disponible</p>
            <p className="mt-1 font-display text-3xl font-extrabold">{wallet ? currency(Number(wallet.solde)) : "Chargement..."}</p>
          </div>

          <div className="space-y-2">
            <Label>Montant à retirer</Label>
            <div className="relative">
              <Input
                type="number"
                placeholder="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="h-16 text-3xl font-display font-bold"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 font-semibold text-muted-foreground">Ar</span>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Agence de retrait</Label>
            <select className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
              <option>MadaVola Analakely</option>
              <option>MadaVola Tana Water Front</option>
              <option>MadaVola Toamasina</option>
            </select>
          </div>

          <div className="rounded-xl bg-warning/10 p-4 text-sm">
            <p className="font-semibold text-warning">Validation par l'administrateur</p>
            <p className="mt-1 text-muted-foreground">
              Délai de traitement : 1 à 24 heures. Présentez votre pièce d'identité à l'agent.
            </p>
          </div>

          <Button
            size="lg"
            className="w-full bg-gradient-gold text-gold-foreground shadow-gold"
            onClick={submit}
            disabled={loading}
          >
            <Banknote className="h-4 w-4" />
            {loading ? "Envoi..." : "Soumettre la demande"}
          </Button>
        </div>

        <div className="space-y-3 rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Demandes récentes</h3>
          {withdrawals.filter((tx) => tx.type_transaction === "retrait").slice(0, 3).map((r) => (
            <div key={r.id_transaction} className="flex items-center justify-between rounded-xl bg-muted/40 p-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-success/10 text-success">
                  <Clock className="h-4 w-4" />
                </div>
                <div className="text-sm">
                  <p className="font-semibold">{currency(Number(r.montant))}</p>
                  <p className="text-xs text-muted-foreground">{new Date(r.date_transaction).toLocaleDateString("fr-FR")}</p>
                </div>
              </div>
              <span className="rounded-full bg-success/10 px-2 py-0.5 text-[10px] font-semibold text-success">
                {r.status.replace("_", " ")}
              </span>
            </div>
          ))}

          <div className="rounded-xl bg-accent/40 p-4 text-sm">
            <Building2 className="mb-2 h-4 w-4 text-primary" />
            <p className="font-semibold">3 agences proches</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Analakely · Water Front · Toamasina
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MerchantWithdraw;
