import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, ShieldCheck, User } from "lucide-react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthAPI, formatApiError } from "@/services/api";
import { useAuthStore } from "@/hooks/useAuthStore";
import { toast } from "sonner";

const Login = () => {
  const navigate = useNavigate();
  const { setPendingUsername } = useAuthStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!username.trim() || !password.trim()) {
      toast.error("Champs requis", { description: "Veuillez remplir tous les champs." });
      return;
    }

    setLoading(true);
    try {
      const response = await AuthAPI.connexion(username.trim(), password);
      setPendingUsername(username.trim());
      toast.success("Identifiants vérifiés", {
        description: response.otp_dev ? `OTP dev: ${response.otp_dev}` : "Entrez le code OTP reçu.",
      });
      navigate("/otp");
    } catch (error) {
      toast.error("Échec de connexion", { description: formatApiError(error, "Identifiants incorrects.") });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-hero px-4 py-8 text-primary-foreground">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-md flex-col justify-center">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo variant="light" size="lg" />
          <span className="rounded-full border border-primary-foreground/20 bg-primary-foreground/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest">
            Made in Madagascar · 2026
          </span>
        </div>

        <form onSubmit={submit} className="rounded-2xl bg-card p-6 text-foreground shadow-elegant">
          <h1 className="font-display text-2xl font-extrabold">Connexion</h1>
          <p className="mt-1 text-sm text-muted-foreground">Accédez à votre portefeuille sécurisé.</p>

          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>Nom d'utilisateur</Label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input className="pl-9" value={username} onChange={(e) => setUsername(e.target.value)} autoCapitalize="none" />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Mot de passe</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  className="px-9"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label="Afficher le mot de passe"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-3 rounded-xl bg-accent/50 p-3 text-sm">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <span>Un code OTP sera envoyé après vérification des identifiants.</span>
          </div>

          <Button type="submit" size="lg" disabled={loading} className="mt-6 w-full bg-gradient-primary">
            {loading ? "Connexion..." : "Se connecter"}
          </Button>

          <p className="mt-5 text-center text-sm text-muted-foreground">
            Pas encore de compte ?{" "}
            <Link to="/register" className="font-semibold text-primary">
              Créer un compte
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
};

export default Login;
