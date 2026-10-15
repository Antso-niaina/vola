import { ArrowDownLeft, ArrowUpRight, Store, PiggyBank, Banknote } from "lucide-react";
import { Transaction, currency } from "@/lib/apiMappers";
import { cn } from "@/lib/utils";

interface Props {
  transactions: Transaction[];
  perspective?: "user" | "merchant";
}

const typeConfig = {
  envoi: { icon: ArrowUpRight, label: "Envoi", color: "text-destructive", bg: "bg-destructive/10", sign: "-" },
  reception: { icon: ArrowDownLeft, label: "Réception", color: "text-success", bg: "bg-success/10", sign: "+" },
  paiement: { icon: Store, label: "Paiement", color: "text-destructive", bg: "bg-destructive/10", sign: "-" },
  depot: { icon: PiggyBank, label: "Dépôt", color: "text-success", bg: "bg-success/10", sign: "+" },
  retrait: { icon: Banknote, label: "Retrait", color: "text-warning", bg: "bg-warning/10", sign: "-" },
} as const;

const statusBadge = {
  validée: "bg-success/10 text-success",
  en_attente: "bg-warning/15 text-warning",
  rejetée: "bg-destructive/10 text-destructive",
};

export const TransactionList = ({ transactions, perspective = "user" }: Props) => {
  return (
    <div className="divide-y divide-border">
      {transactions.map((tx) => {
        const cfg = typeConfig[tx.type];
        const Icon = cfg.icon;
        const isCredit = perspective === "merchant" || cfg.sign === "+";
        return (
          <div key={tx.id} className="flex items-center gap-4 py-4 transition-smooth hover:bg-muted/40 hover:px-2 hover:rounded-lg">
            <div className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-xl", cfg.bg)}>
              <Icon className={cn("h-5 w-5", cfg.color)} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="truncate font-semibold text-foreground">{tx.counterparty}</p>
                <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide", statusBadge[tx.status])}>
                  {tx.status.replace("_", " ")}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                {cfg.label} · {tx.date} · {tx.reference}
              </p>
            </div>
            <p className={cn("shrink-0 font-display text-base font-bold", isCredit ? "text-success" : "text-foreground")}>
              {isCredit ? "+" : "-"}
              {currency(tx.amount)}
            </p>
          </div>
        );
      })}
    </div>
  );
};
