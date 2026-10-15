import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Store, User, Wallet } from "lucide-react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthAPI, formatApiError, Role } from "@/services/api";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const Register = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<Role>("client");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    username: "",
    email: "",
    telephone: "",
    nom_boutique: "",
    password: "",
    confirmPassword: "",
  });

  const set = (key: keyof typeof form) => (value: string) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.username || !form.email || !form.password || !form.telephone) {
      toast.error("Champs requis", { description: "Veuillez remplir tous les champs obligatoires." });
      return;
    }
    if (form.password !== form.confirmPassword) {
      toast.error("Erreur", { description: "Les mots de passe ne correspondent pas." });
      return;
    }
    if (role === "commercant" && !form.nom_boutique) {
      toast.error("Champ requis", { description: "Le nom de la boutique est requis pour les commerçants." });
      return;
    }

    setLoading(true);
    try {
      await AuthAPI.inscription({
        username: form.username.trim(),
        email: form.email.trim(),
        telephone: form.telephone.trim(),
        password: form.password,
        role,
        nom_boutique: role === "commercant" ? form.nom_boutique.trim() : undefined,
      });
      toast.success("Compte créé", { description: "Vous pouvez maintenant vous connecter." });
      navigate("/");
    } catch (error) {
      toast.error("Échec", { description: formatApiError(error, "Erreur lors de l'inscription.") });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-hero px-4 py-8 text-primary-foreground">
      <div className="mx-auto w-full max-w-2xl">
        <div className="mb-6 flex items-center justify-between">
          <Logo variant="light" />
          <Button variant="outline" className="border-primary-foreground/25 bg-primary-foreground/10 text-primary-foreground" asChild>
            <Link to="/">Retour</Link>
          </Button>
        </div>

        <form onSubmit={submit} className="rounded-2xl bg-card p-6 text-foreground shadow-elegant">
          <h1 className="font-display text-2xl font-extrabold">Créer un compte</h1>
          <p className="mt-1 text-sm text-muted-foreground">Rejoignez MadaVola gratuitement.</p>

          <div className="mt-5 grid grid-cols-2 gap-3">
            {[
              { key: "client" as Role, label: "Client", icon: Wallet, desc: "Envoyer, recevoir, payer" },
              { key: "commercant" as Role, label: "Commerçant", icon: Store, desc: "Recevoir des paiements QR" },
            ].map((item) => {
              const Icon = item.icon;
              const active = role === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setRole(item.key)}
                  className={cn("rounded-xl border p-4 text-left transition-smooth", active ? "border-primary bg-primary/10" : "border-border")}
                >
                  <Icon className={cn("h-5 w-5", active ? "text-primary" : "text-muted-foreground")} />
                  <p className="mt-2 font-semibold">{item.label}</p>
                  <p className="text-xs text-muted-foreground">{item.desc}</p>
                </button>
              );
            })}
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <Field label="Nom d'utilisateur *" value={form.username} onChange={set("username")} />
            <Field label="Email *" type="email" value={form.email} onChange={set("email")} />
            <Field label="Téléphone *" value={form.telephone} onChange={set("telephone")} />
            {role === "commercant" && <Field label="Nom de la boutique *" value={form.nom_boutique} onChange={set("nom_boutique")} />}
            <Field label="Mot de passe *" type="password" value={form.password} onChange={set("password")} />
            <Field label="Confirmer le mot de passe *" type="password" value={form.confirmPassword} onChange={set("confirmPassword")} />
          </div>

          <Button type="submit" size="lg" disabled={loading} className="mt-6 w-full bg-gradient-primary">
            <User className="h-4 w-4" />
            {loading ? "Création..." : "Créer mon compte"}
          </Button>
        </form>
      </div>
    </main>
  );
};

const Field = ({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) => (
  <div className="space-y-2">
    <Label>{label}</Label>
    <Input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
  </div>
);

export default Register;
