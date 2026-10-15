import { Bell, Lock, ShieldCheck, User } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/hooks/useAuthStore";
import { AuthAPI, CompteAPI, formatApiError } from "@/services/api";
import { initials } from "@/lib/apiMappers";
import { toast } from "sonner";

const MerchantProfile = () => {
  const { user, refreshProfile } = useAuthStore();
  const [form, setForm] = useState({
    nom_boutique: user?.nom_boutique ?? "",
    telephone: user?.telephone ?? "",
    email: user?.email ?? "",
  });
  const [password, setPassword] = useState({ ancien: "", nouveau: "" });

  const saveProfile = async () => {
    try {
      await CompteAPI.updateProfil(form);
      await refreshProfile();
      toast.success("Profil mis à jour");
    } catch (error) {
      toast.error("Mise à jour impossible", { description: formatApiError(error) });
    }
  };

  const changePassword = async () => {
    if (!password.ancien || !password.nouveau) {
      toast.error("Champs requis", { description: "Veuillez remplir les deux mots de passe." });
      return;
    }
    try {
      await AuthAPI.changerMotDePasse(password.ancien, password.nouveau);
      setPassword({ ancien: "", nouveau: "" });
      toast.success("Mot de passe changé");
    } catch (error) {
      toast.error("Mise à jour impossible", { description: formatApiError(error) });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Profil du commerce</h1>
        <p className="mt-1 text-sm text-muted-foreground">Gérez vos informations et vos préférences de sécurité.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-6 text-center shadow-card-soft">
          <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-gradient-primary font-display text-3xl font-extrabold text-primary-foreground shadow-elegant">
            {initials(user?.nom_boutique || user?.username)}
          </div>
          <p className="mt-4 font-display text-xl font-bold">{user?.nom_boutique || user?.username}</p>
          <p className="text-sm text-muted-foreground">{user?.email}</p>
          <span className="mt-3 inline-block rounded-full bg-success/10 px-3 py-1 text-xs font-semibold text-success">
            Vérifié · KYC validé
          </span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft lg:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <User className="h-4 w-4 text-primary" />
            <h3 className="font-display text-lg font-bold">Informations</h3>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Nom du commerce</Label>
              <Input value={form.nom_boutique} onChange={(e) => setForm((current) => ({ ...current, nom_boutique: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Propriétaire</Label>
              <Input value={user?.username ?? ""} disabled />
            </div>
            <div className="space-y-2">
              <Label>Téléphone</Label>
              <Input value={form.telephone} onChange={(e) => setForm((current) => ({ ...current, telephone: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>ID portefeuille</Label>
              <Input value={`MVM-${user?.id_utilisateur ?? "----"}`} disabled />
            </div>
          </div>
          <Button className="mt-5 bg-gradient-primary" onClick={saveProfile}>Enregistrer</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <div className="mb-4 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <h3 className="font-display text-lg font-bold">Sécurité</h3>
          </div>
          {[
            { l: "Authentification à deux facteurs (2FA)", on: true },
            { l: "Connexion par OTP SMS", on: true },
            { l: "Notification de chaque vente", on: true },
            { l: "Verrouillage automatique après 3 min", on: false },
          ].map((s) => (
            <div key={s.l} className="flex items-center justify-between border-b border-border py-3 last:border-0">
              <span className="text-sm">{s.l}</span>
              <Switch defaultChecked={s.on} />
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-card-soft">
          <div className="mb-4 flex items-center gap-2">
            <Bell className="h-4 w-4 text-primary" />
            <h3 className="font-display text-lg font-bold">Mot de passe</h3>
          </div>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label>Mot de passe actuel</Label>
              <Input type="password" value={password.ancien} onChange={(e) => setPassword((current) => ({ ...current, ancien: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Nouveau mot de passe</Label>
              <Input type="password" value={password.nouveau} onChange={(e) => setPassword((current) => ({ ...current, nouveau: e.target.value }))} />
            </div>
            <Button variant="outline" className="w-full" onClick={changePassword}>
              <Lock className="h-4 w-4" />
              Mettre à jour
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MerchantProfile;
