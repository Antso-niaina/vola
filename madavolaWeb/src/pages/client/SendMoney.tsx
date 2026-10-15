import { useState } from "react";
import { ArrowRight, Search, Send, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { currency } from "@/lib/apiMappers";
import { toast } from "sonner";
import { formatApiError, PortefeuilleAPI } from "@/services/api";

const SendMoney = () => {
  const [selected, setSelected] = useState<string | null>(null);
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipient.trim() || !amount || Number(amount) <= 0) {
      toast.error("Champs invalides", { description: "Veuillez saisir un destinataire et un montant supérieur à 0." });
      return;
    }

    setLoading(true);
    try {
      const response = await PortefeuilleAPI.transfert(recipient.trim(), Number(amount), note.trim() || undefined);
      toast.success("Transfert envoyé", { description: response.detail });
      setRecipient("");
      setAmount("");
      setNote("");
    } catch (error) {
      toast.error("Transfert impossible", { description: formatApiError(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Envoyer de l'argent</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Transfert instantané vers un autre utilisateur MadaVola.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        
        <form onSubmit={onSubmit} className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-card-soft lg:col-span-3">
          <div className="space-y-2">
            <Label>Numéro ou ID portefeuille du destinataire</Label>
            <Input placeholder="+261 34 ..." value={recipient} onChange={(e) => setRecipient(e.target.value)} required />
          </div>

          <div className="space-y-2">
            <Label>Montant (Ariary)</Label>
            <div className="relative">
              <Input
                type="number"
                placeholder="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="h-16 text-3xl font-display font-bold"
                required
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 font-semibold text-muted-foreground">Ar</span>
            </div>
            <div className="flex flex-wrap gap-2 pt-1">
              {[10000, 50000, 100000, 250000].map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setAmount(String(v))}
                  className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-muted-foreground transition-smooth hover:border-primary hover:text-primary"
                >
                  +{currency(v)}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Motif (optionnel)</Label>
            <Textarea placeholder="Ex : Remboursement déjeuner" value={note} onChange={(e) => setNote(e.target.value)} />
          </div>

          <div className="flex items-center gap-3 rounded-xl bg-accent/40 p-3 text-sm">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <span>Confirmation par code OTP requise avant envoi.</span>
          </div>

          <Button type="submit" size="lg" className="w-full bg-gradient-primary shadow-elegant" disabled={loading}>
            <Send className="h-4 w-4" />
            {loading ? "Envoi..." : "Envoyer maintenant"}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        
        <div className="space-y-3 rounded-2xl border border-border bg-card p-6 shadow-card-soft lg:col-span-2">
          <h3 className="font-display text-lg font-bold">Contacts récents</h3>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input className="pl-9" placeholder="Rechercher un contact" />
          </div>
          <div className="space-y-2">
            {[
              { id: "manual", name: "Saisie manuelle", phone: recipient || "+261 ...", initials: "MV" },
            ].map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelected(c.id)}
                className={`flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-smooth ${
                  selected === c.id
                    ? "border-primary bg-primary/5"
                    : "border-transparent bg-muted/30 hover:bg-muted/60"
                }`}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-primary font-semibold text-primary-foreground">
                  {c.initials}
                </div>
                <div className="flex-1">
                  <p className="font-semibold">{c.name}</p>
                  <p className="text-xs text-muted-foreground">{c.phone}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SendMoney;
