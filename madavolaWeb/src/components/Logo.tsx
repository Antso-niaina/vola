import { Wallet } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  variant?: "default" | "light";
  showText?: boolean;
}

export const Logo = ({ className, variant = "default", showText = true }: LogoProps) => {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <div className="relative">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
          <Wallet className="h-5 w-5 text-primary-foreground" strokeWidth={2.5} />
        </div>
        <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-gradient-gold shadow-gold" />
      </div>
      {showText && (
        <div className="flex flex-col leading-none">
          <span
            className={cn(
              "font-display text-xl font-extrabold tracking-tight",
              variant === "light" ? "text-primary-foreground" : "text-foreground"
            )}
          >
            MadaVola
          </span>
          <span
            className={cn(
              "text-[10px] font-medium uppercase tracking-[0.18em]",
              variant === "light" ? "text-primary-foreground/60" : "text-muted-foreground"
            )}
          >
            Portefeuille virtuel
          </span>
        </div>
      )}
    </div>
  );
};
