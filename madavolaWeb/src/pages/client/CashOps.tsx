import { useState } from "react";
import { Banknote, Building2, Clock, PiggyBank } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { currency } from "@/lib/apiMappers";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { formatApiError, TransactionAPI } from "@/services/api";

const agencies = [
  { name: "MadaVola Analakely", addr: "Lot 12 – Antananarivo", hours: "Lun-Sam · 8h-17h" },
  { name: "MadaVola Tana Water Front", addr: "Ambodivona", hours: "Tous les jours · 9h-19h" },
  { name: "MadaVola Toamasina", addr: "Bd Joffre", hours: "Lun-Ven · 8h-16h" },
];

const CashOps = () => {
  const [params] = useSearchParams();
  const initial = params.get("op") === "retrait" ? "retrait" : "depot";
  const [op, setOp] = useState<"depot" | "retrait">(initial);
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!amount || Number(amount) <= 0) {
      toast.error("Montant invalide", { description: "Le montant doit être supérieur à 0." });
      return;
    }

    setLoading(true);
    try {
      const response =
        op === "depot"
          ? await TransactionAPI.demandeDepot(Number(amount))
          : await TransactionAPI.demandeRetrait(Number(amount));
      toast.success(`Demande de ${op} envoyée`, { description: response.detail });
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
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Cash · Dépôt & Retrait</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Convertissez votre argent physique ↔ MadaVola dans une agence partenaire.
        </p>
      </div>

      
      <div className="grid grid-cols-2 gap-3 rounded-2xl border border-border bg-card p-2 shadow-card-soft">
        {(["depot", "retrait"] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setOp(mode)}
            className={cn(
              "flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition-smooth",
              op === mode
                ? mode === "depot"
                  ? "bg-gradient-primary text-primary-foreground shadow-elegant"
                  : "bg-gradient-gold text-gold-foreground shadow-gold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {mode === "depot" ? <PiggyBank className="h-4 w-4" /> : <Banknote className="h-4 w-4" />}
            {mode === "depot" ? "Déposer du cash" : "Retirer en cash"}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">
            {op === "depot" ? "Demande de dépôt" : "Demande de retrait"}
          </h3>

          <div className="space-y-2">
            <Label>Montant (Ar)</Label>
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
            <Label>Agence</Label>
            <select className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
              {agencies.map((a) => (
                <option key={a.name}>{a.name}</option>
              ))}
            </select>
          </div>

          <div className="rounded-xl bg-accent/40 p-4 text-sm">
            <p className="font-semibold">Référence générée à la confirmation</p>
            <p className="mt-1 text-muted-foreground">
              Présentez cette référence à l'agent. La validation par l'administrateur est{" "}
              <span className="font-semibold text-foreground">obligatoire</span>.
            </p>
          </div>

          <Button
            size="lg"
            disabled={loading}
            className={cn(
              "w-full",
              op === "depot" ? "bg-gradient-primary shadow-elegant" : "bg-gradient-gold text-gold-foreground shadow-gold"
            )}
            onClick={submit}
          >
            {loading ? "Soumission..." : "Soumettre la demande"}
          </Button>
        </div>

        <div className="space-y-4 rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Agences MadaVola</h3>
          {agencies.map((a) => (
            <div key={a.name} className="flex gap-3 rounded-xl bg-muted/40 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold">{a.name}</p>
                <p className="text-xs text-muted-foreground">{a.addr}</p>
                <p className="mt-1 inline-flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {a.hours}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CashOps;
