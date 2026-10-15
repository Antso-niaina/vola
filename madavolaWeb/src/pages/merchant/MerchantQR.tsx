import { QRCodeSVG } from "qrcode.react";
import { Download, Printer, RefreshCw, Share2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/Logo";
import { useAuthStore } from "@/hooks/useAuthStore";
import { CommercantAPI } from "@/services/api";

const MerchantQR = () => {
  const { user } = useAuthStore();
  const { data, isLoading, refetch } = useQuery({ queryKey: ["merchant-qr"], queryFn: CommercantAPI.genererQR });
  const merchantName = user?.nom_boutique || user?.username || "Commerce MadaVola";
  const qrValue = data?.code_qr ?? "";

  const shareQr = async () => {
    if (!qrValue) return;
    if (navigator.share) {
      await navigator.share({ title: "Mon QR code MadaVola", text: `Mon QR MadaVola : ${qrValue}` });
      return;
    }
    await navigator.clipboard.writeText(qrValue);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Mon QR code commerçant</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Affichez ce code en caisse. Vos clients le scannent pour vous payer instantanément.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        
        <div className="flex justify-center">
          <div className="w-full max-w-sm overflow-hidden rounded-3xl bg-gradient-card p-1 shadow-elegant">
            <div className="rounded-[1.4rem] bg-card p-6 text-center">
              <Logo />
              <p className="mt-6 text-xs font-semibold uppercase tracking-widest text-muted-foreground">Payer</p>
              <p className="font-display text-2xl font-bold">{merchantName}</p>

              <div className="my-5 flex justify-center rounded-2xl bg-white p-5 shadow-card-soft">
                {isLoading ? (
                  <div className="flex h-[220px] w-[220px] items-center justify-center text-sm text-muted-foreground">Chargement...</div>
                ) : (
                  <QRCodeSVG
                    value={qrValue || "QR indisponible"}
                    size={220}
                    level="H"
                    fgColor="#0f3a2a"
                    bgColor="#ffffff"
                  />
                )}
              </div>

              <p className="font-mono text-sm text-muted-foreground">{qrValue || "QR indisponible"}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Ouvrez l'app MadaVola → <span className="font-semibold">Payer</span> → Scanner
              </p>
            </div>
          </div>
        </div>

        
        <div className="space-y-5">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft">
            <h3 className="font-display text-lg font-bold">Actions rapides</h3>
            <div className="mt-4 grid grid-cols-3 gap-3">
              <Button variant="outline" className="flex-col h-auto py-4" disabled={!qrValue}>
                <Download className="h-5 w-5" />
                <span className="mt-1 text-xs">Télécharger</span>
              </Button>
              <Button variant="outline" className="flex-col h-auto py-4" onClick={() => window.print()} disabled={!qrValue}>
                <Printer className="h-5 w-5" />
                <span className="mt-1 text-xs">Imprimer</span>
              </Button>
              <Button variant="outline" className="flex-col h-auto py-4" onClick={shareQr} disabled={!qrValue}>
                <Share2 className="h-5 w-5" />
                <span className="mt-1 text-xs">Partager</span>
              </Button>
            </div>
            <Button variant="outline" className="mt-3 w-full" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4" />
              Régénérer
            </Button>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft">
            <h3 className="font-display text-lg font-bold">Informations</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between border-b border-border pb-2">
                <dt className="text-muted-foreground">Nom du commerce</dt>
                <dd className="font-semibold">{merchantName}</dd>
              </div>
              <div className="flex justify-between border-b border-border pb-2">
                <dt className="text-muted-foreground">Propriétaire</dt>
                <dd className="font-semibold">{user?.username || "Compte commerçant"}</dd>
              </div>
              <div className="flex justify-between border-b border-border pb-2">
                <dt className="text-muted-foreground">ID portefeuille</dt>
                <dd className="font-mono">{data?.id_qr ? `QR-${data.id_qr}` : "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Statut</dt>
                <dd>
                  <span className="rounded-full bg-success/10 px-2.5 py-0.5 text-xs font-semibold text-success">
                    Actif & vérifié
                  </span>
                </dd>
              </div>
            </dl>
          </div>

          <div className="rounded-2xl bg-gradient-hero p-6 text-primary-foreground">
            <p className="text-xs font-semibold uppercase tracking-widest opacity-70">Astuce</p>
            <p className="mt-2 font-display text-lg font-bold">
              Ce QR est unique et lié à votre commerce. Il est non modifiable et vérifié par MadaVola.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MerchantQR;
