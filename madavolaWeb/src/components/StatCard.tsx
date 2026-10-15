import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: { value: string; positive?: boolean };
  variant?: "default" | "primary" | "gold";
  className?: string;
}

export const StatCard = ({ label, value, icon: Icon, trend, variant = "default", className }: StatCardProps) => {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border p-5 transition-smooth hover:shadow-elegant",
        variant === "default" && "border-border bg-card shadow-card-soft",
        variant === "primary" && "border-transparent bg-gradient-card text-primary-foreground shadow-elegant",
        variant === "gold" && "border-transparent bg-gradient-gold text-gold-foreground shadow-gold",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p
            className={cn(
              "text-xs font-semibold uppercase tracking-wider",
              variant === "default" ? "text-muted-foreground" : "opacity-80"
            )}
          >
            {label}
          </p>
          <p className="mt-2 font-display text-2xl font-bold tracking-tight md:text-3xl">{value}</p>
          {trend && (
            <div
              className={cn(
                "mt-2 inline-flex items-center gap-1 text-xs font-medium",
                variant === "default"
                  ? trend.positive
                    ? "text-success"
                    : "text-destructive"
                  : "opacity-90"
              )}
            >
              {trend.positive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              <span>{trend.value}</span>
            </div>
          )}
        </div>
        <div
          className={cn(
            "flex h-11 w-11 items-center justify-center rounded-xl",
            variant === "default" && "bg-primary/10 text-primary",
            variant === "primary" && "bg-primary-foreground/15 text-primary-foreground",
            variant === "gold" && "bg-gold-foreground/15 text-gold-foreground"
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
};
