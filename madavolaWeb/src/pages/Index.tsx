import { Link } from "react-router-dom";
import {
  Wallet,
  ShieldCheck,
  Zap,
  QrCode,
  Smartphone,
  Users,
  ArrowRight,
  Store,
  ShieldAlert,
  Sparkles,
  Lock,
  TrendingUp,
} from "lucide-react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";

const features = [
  { icon: Zap, title: "Transactions < 3 sec", desc: "Envoyez et recevez de l'argent instantanément, même en 3G." },
  { icon: ShieldCheck, title: "Sécurité 2FA", desc: "Authentification renforcée et chiffrement bout en bout." },
  { icon: QrCode, title: "Paiement par QR", desc: "Payez chez vos commerçants en scannant simplement leur code." },
  { icon: ShieldAlert, title: "Anti-fraude", desc: "Surveillance des flux par algorithmes Dijkstra & Top-K." },
  { icon: Smartphone, title: "Mobile & Web", desc: "Disponible sur Android, iOS et navigateur. Toujours synchronisé." },
  { icon: Users, title: "Inclusion financière", desc: "Pas besoin de compte bancaire. 100% accessible à Madagascar." },
];

const roles = [
  {
    icon: Wallet,
    title: "Espace Client",
    desc: "Gérez votre portefeuille, envoyez de l'argent, payez par QR.",
    cta: "Entrer comme client",
    to: "/client",
    accent: "from-primary to-primary-glow",
  },
  {
    icon: Store,
    title: "Espace Commerçant",
    desc: "Recevez des paiements, suivez vos ventes, demandez vos retraits.",
    cta: "Entrer comme commerçant",
    to: "/commercant",
    accent: "from-gold to-gold-glow",
  },
  {
    icon: ShieldCheck,
    title: "Console Admin",
    desc: "Validez dépôts/retraits, supervisez les utilisateurs et flux.",
    cta: "Accéder à l'admin",
    to: "/admin",
    accent: "from-primary-glow to-success",
  },
];

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      
      <header className="relative overflow-hidden bg-gradient-hero text-primary-foreground">
        <div className="absolute inset-0 opacity-20" aria-hidden>
          <div className="absolute -left-24 top-12 h-72 w-72 rounded-full bg-primary-glow blur-3xl" />
          <div className="absolute right-0 top-1/2 h-96 w-96 rounded-full bg-gold/30 blur-3xl" />
        </div>

        <div className="container relative z-10">
          <nav className="flex items-center justify-between py-6">
            <Logo variant="light" />
            <div className="hidden gap-2 md:flex">
              <Button variant="ghost" className="text-primary-foreground hover:bg-primary-foreground/10" asChild>
                <a href="#fonctionnalites">Fonctionnalités</a>
              </Button>
              <Button variant="ghost" className="text-primary-foreground hover:bg-primary-foreground/10" asChild>
                <a href="#espaces">Espaces</a>
              </Button>
              <Button className="bg-gold text-gold-foreground hover:bg-gold-glow shadow-gold" asChild>
                <Link to="/client">Ouvrir l'app</Link>
              </Button>
            </div>
          </nav>

          <div className="grid gap-12 py-16 md:py-24 lg:grid-cols-2 lg:items-center">
            <div className="animate-fade-in">
              <span className="inline-flex items-center gap-2 rounded-full border border-primary-foreground/20 bg-primary-foreground/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest">
                <Sparkles className="h-3.5 w-3.5 text-gold" />
                Made in Madagascar · 2026
              </span>
              <h1 className="mt-5 font-display text-4xl font-extrabold leading-[1.05] tracking-tight md:text-6xl">
                Le portefeuille virtuel <span className="text-gradient-gold">malgache</span> qui change les paiements.
              </h1>
              <p className="mt-5 max-w-xl text-base leading-relaxed text-primary-foreground/80 md:text-lg">
                MadaVola convertit votre cash en monnaie virtuelle sécurisée. Envoyez, recevez et payez vos commerçants
                en moins de 3 secondes — sans liquide, sans risque.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Button size="lg" className="bg-gold text-gold-foreground hover:bg-gold-glow shadow-gold" asChild>
                  <Link to="/client">
                    Démarrer maintenant <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="border-primary-foreground/30 bg-primary-foreground/5 text-primary-foreground hover:bg-primary-foreground/15"
                  asChild
                >
                  <a href="#espaces">Découvrir les espaces</a>
                </Button>
              </div>

              <div className="mt-10 grid grid-cols-3 gap-6">
                {[
                  { v: "12 487", l: "Utilisateurs" },
                  { v: "842", l: "Commerçants" },
                  { v: "1.2 Md Ar", l: "Volume traité" },
                ].map((s) => (
                  <div key={s.l}>
                    <p className="font-display text-2xl font-bold text-gold">{s.v}</p>
                    <p className="text-xs uppercase tracking-wider text-primary-foreground/60">{s.l}</p>
                  </div>
                ))}
              </div>
            </div>

            
            <div className="relative mx-auto hidden w-full max-w-sm lg:block">
              <div className="absolute inset-0 -z-10 rounded-[3rem] bg-gradient-gold opacity-30 blur-3xl" />
              <div className="relative rounded-[2.5rem] border border-primary-foreground/15 bg-gradient-to-b from-primary/40 to-primary/10 p-3 shadow-elegant backdrop-blur">
                <div className="overflow-hidden rounded-[2rem] bg-card text-foreground">
                  <div className="bg-gradient-card p-6 text-primary-foreground">
                    <p className="text-xs uppercase tracking-widest opacity-70">Solde actuel</p>
                    <p className="mt-1 font-display text-3xl font-extrabold">1 245 800 Ar</p>
                    <p className="mt-1 text-xs opacity-70">MV-7842-3019</p>
                  </div>
                  <div className="grid grid-cols-4 gap-2 p-4">
                    {[Wallet, QrCode, TrendingUp, Lock].map((I, i) => (
                      <div key={i} className="flex flex-col items-center gap-1 rounded-xl bg-muted/60 p-3">
                        <I className="h-5 w-5 text-primary" />
                        <span className="text-[10px] font-medium text-muted-foreground">Action</span>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-3 p-4 pt-0">
                    {[
                      { n: "Hery R.", a: "+120 000", c: "text-success" },
                      { n: "Épicerie Tsara", a: "-45 500", c: "text-foreground" },
                      { n: "Mialy V.", a: "-80 000", c: "text-foreground" },
                    ].map((t) => (
                      <div key={t.n} className="flex items-center justify-between border-b border-border pb-2 last:border-0">
                        <div className="flex items-center gap-2">
                          <div className="h-8 w-8 rounded-full bg-accent" />
                          <p className="text-sm font-medium">{t.n}</p>
                        </div>
                        <p className={`text-sm font-bold ${t.c}`}>{t.a} Ar</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      
      <section id="fonctionnalites" className="container py-20">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary">Pourquoi MadaVola</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-4xl">
            Pensé pour la réalité malgache
          </h2>
          <p className="mt-3 text-muted-foreground">
            Sécurité bancaire, simplicité mobile, et gratuité d'usage pour fluidifier votre quotidien.
          </p>
        </div>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-2xl border border-border bg-card p-6 shadow-card-soft transition-smooth hover:-translate-y-1 hover:border-primary/30 hover:shadow-elegant"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-display text-lg font-bold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      
      <section id="espaces" className="bg-gradient-surface py-20">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-primary">Trois espaces, un écosystème</p>
            <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-4xl">
              Choisissez votre espace MadaVola
            </h2>
          </div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {roles.map((r) => (
              <Link
                key={r.to}
                to={r.to}
                className="group relative overflow-hidden rounded-3xl border border-border bg-card p-8 shadow-card-soft transition-smooth hover:-translate-y-2 hover:border-primary/40 hover:shadow-elegant"
              >
                <div
                  className={`absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br ${r.accent} opacity-15 blur-2xl transition-smooth group-hover:opacity-30`}
                />
                <div className={`mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${r.accent} text-primary-foreground shadow-elegant`}>
                  <r.icon className="h-6 w-6" />
                </div>
                <h3 className="font-display text-2xl font-bold">{r.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{r.desc}</p>
                <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary transition-smooth group-hover:gap-3">
                  {r.cta} <ArrowRight className="h-4 w-4" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-border bg-card py-10">
        <div className="container flex flex-col items-center justify-between gap-4 md:flex-row">
          <Logo />
          <p className="text-sm text-muted-foreground">
            © 2026 MadaVola · Plateforme de paiement électronique malgache.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
