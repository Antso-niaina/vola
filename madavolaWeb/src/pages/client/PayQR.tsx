import { useState } from "react";
import { QrCode, ScanLine, Store, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { currency } from "@/lib/apiMappers";
import { toast } from "sonner";
import { CommercantAPI, formatApiError } from "@/services/api";
import { useQueryClient } from "@tanstack/react-query";

const PayQR = () => {
  const queryClient = useQueryClient();
  const [scanning, setScanning] = useState(false);
  const [codeQr, setCodeQr] = useState("");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!codeQr.trim() || !amount || Number(amount) <= 0) {
      toast.error("Champs invalides", { description: "Veuillez saisir le code QR et un montant supérieur à 0." });
      return;
    }

    setLoading(true);
    try {
      const payment = await CommercantAPI.paiementQR(codeQr.trim(), Number(amount));
      queryClient.invalidateQueries({ queryKey: ["wallet"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      toast.success("Paiement effectué", { description: `Référence ${payment.reference}` });
      setAmount("");
    } catch (error) {
      toast.error("Paiement impossible", { description: formatApiError(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Payer un commerçant</h1>
        <p className="mt-1 text-sm text-muted-foreground">Scannez le QR code ou saisissez l'ID du commerçant.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        
        <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Scanner un QR code</h3>
          <div className="relative mt-4 flex aspect-square items-center justify-center overflow-hidden rounded-2xl bg-gradient-hero text-primary-foreground">
            <div className="absolute inset-6 rounded-2xl border-2 border-dashed border-primary-foreground/30" />
            <div className="absolute inset-x-10 top-1/2 h-px bg-gradient-to-r from-transparent via-gold to-transparent" />
            <div className="text-center">
              <QrCode className={`mx-auto h-16 w-16 opacity-60 ${scanning ? "animate-pulse" : ""}`} />
              <p className="mt-3 text-sm opacity-80">{scanning ? "Recherche en cours..." : "Pointez la caméra vers un QR code"}</p>
            </div>
          </div>
          <Button
            onClick={() => {
              setScanning(true);
              setTimeout(() => {
                setScanning(false);
                toast.info("Scanner caméra non disponible dans cette maquette", {
                  description: "Collez le code QR généré par le commerçant dans la saisie manuelle.",
                });
              }, 1400);
            }}
            className="mt-4 w-full bg-gradient-primary"
          >
            <ScanLine className="h-4 w-4" />
            Activer le scanner
          </Button>
        </div>

        
        <div className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <h3 className="font-display text-lg font-bold">Saisie manuelle</h3>

          <div className="space-y-2">
            <Label>ID commerçant</Label>
            <div className="relative">
              <Store className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="pl-9" placeholder="Code QR commerçant" value={codeQr} onChange={(e) => setCodeQr(e.target.value)} />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Montant à payer</Label>
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

          <div className="rounded-xl bg-gradient-card p-4 text-primary-foreground">
            <p className="text-xs uppercase tracking-widest opacity-70">Récapitulatif</p>
            <div className="mt-2 space-y-1 text-sm">
              <div className="flex justify-between"><span className="opacity-80">Code QR</span><span className="max-w-40 truncate font-semibold">{codeQr || "—"}</span></div>
              <div className="flex justify-between"><span className="opacity-80">Frais</span><span className="font-semibold">0 Ar</span></div>
              <div className="mt-2 flex items-end justify-between border-t border-primary-foreground/20 pt-2">
                <span className="opacity-80">Total</span>
                <span className="font-display text-xl font-extrabold text-gold">{currency(Number(amount) || 0)}</span>
              </div>
            </div>
          </div>

          <Button
            size="lg"
            className="w-full bg-gradient-gold text-gold-foreground shadow-gold hover:opacity-95"
            disabled={loading}
            onClick={submit}
          >
            <Zap className="h-4 w-4" />
            {loading ? "Paiement..." : "Confirmer le paiement"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PayQR;
