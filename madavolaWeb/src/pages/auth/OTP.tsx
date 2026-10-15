import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { MailOpen, ShieldCheck } from "lucide-react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { AuthAPI, formatApiError } from "@/services/api";
import { homeForRole } from "@/components/ProtectedRoute";
import { useAuthStore } from "@/hooks/useAuthStore";
import { toast } from "sonner";

const OTP_LENGTH = 6;

const OTP = () => {
  const navigate = useNavigate();
  const { pendingUsername, setSession } = useAuthStore();
  const [otp, setOtp] = useState<string[]>(Array(OTP_LENGTH).fill(""));
  const [loading, setLoading] = useState(false);
  const refs = useRef<Array<HTMLInputElement | null>>([]);

  useEffect(() => {
    if (!pendingUsername) navigate("/");
  }, [pendingUsername, navigate]);

  const change = (value: string, index: number) => {
    const digit = value.replace(/[^0-9]/g, "").slice(-1);
    setOtp((current) => current.map((item, i) => (i === index ? digit : item)));
    if (digit && index < OTP_LENGTH - 1) refs.current[index + 1]?.focus();
    if (!digit && index > 0) refs.current[index - 1]?.focus();
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const code = otp.join("");
    if (code.length < OTP_LENGTH || !pendingUsername) {
      toast.error("Code incomplet", { description: "Veuillez entrer les 6 chiffres du code OTP." });
      return;
    }

    setLoading(true);
    try {
      const response = await AuthAPI.verifierOTP(pendingUsername, code);
      const user = await setSession(response.access_token, response.refresh_token, response.role, response.username);
      navigate(homeForRole(user.role), { replace: true });
    } catch (error) {
      toast.error("Vérification échouée", { description: formatApiError(error, "Code OTP invalide ou expiré.") });
      setOtp(Array(OTP_LENGTH).fill(""));
      refs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-hero px-4 py-8 text-primary-foreground">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-md flex-col justify-center">
        <div className="mb-8 flex justify-center">
          <Logo variant="light" />
        </div>

        <form onSubmit={submit} className="rounded-2xl bg-card p-6 text-center text-foreground shadow-elegant">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-primary text-primary-foreground shadow-glow">
            <MailOpen className="h-7 w-7" />
          </div>
          <h1 className="mt-5 font-display text-2xl font-extrabold">Code de vérification</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Un code OTP à 6 chiffres a été envoyé pour <span className="font-semibold text-primary">{pendingUsername}</span>.
          </p>

          <div className="mt-6 flex justify-center gap-2">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(node) => {
                  refs.current[index] = node;
                }}
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(event) => change(event.target.value, index)}
                className="h-12 w-11 rounded-lg border border-border bg-muted text-center text-xl font-bold outline-none transition-smooth focus:border-primary"
              />
            ))}
          </div>

          <div className="mt-5 flex items-center gap-3 rounded-xl bg-accent/50 p-3 text-left text-sm">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <span>Ce code expire dans 5 minutes. Ne le partagez jamais.</span>
          </div>

          <Button type="submit" size="lg" disabled={loading} className="mt-6 w-full bg-gradient-primary">
            {loading ? "Vérification..." : "Vérifier le code"}
          </Button>

          <Link to="/" className="mt-5 inline-block text-sm text-muted-foreground">
            Retour à la connexion
          </Link>
        </form>
      </div>
    </main>
  );
};

export default OTP;
