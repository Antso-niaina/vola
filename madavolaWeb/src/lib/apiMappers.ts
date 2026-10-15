import { ApiTransaction, MerchantPayment, PendingDeposit, PendingWithdrawal, UserProfile } from "@/services/api";

export type TxType = "envoi" | "reception" | "paiement" | "depot" | "retrait";
export type TxStatus = "validée" | "en_attente" | "rejetée";

export interface Transaction {
  id: string;
  type: TxType;
  counterparty: string;
  amount: number;
  date: string;
  status: TxStatus;
  reference: string;
}

export const currency = (n: number) =>
  new Intl.NumberFormat("fr-MG", { maximumFractionDigits: 0 }).format(n) + " Ar";

export const initials = (name = "") =>
  name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase() || "MV";

export const displayName = (profile?: UserProfile | null) => {
  if (!profile) return "MadaVola";
  if (profile.nom_boutique) return profile.nom_boutique;
  const first = profile.user?.first_name ?? "";
  const last = profile.user?.last_name ?? "";
  return `${first} ${last}`.trim() || profile.user?.username || profile.username || "MadaVola";
};

const statusMap: Record<string, Transaction["status"]> = {
  validee: "validée",
  en_attente: "en_attente",
  refusee: "rejetée",
};

export const mapTransaction = (tx: ApiTransaction, username?: string): Transaction => {
  const isSender = tx.expediteur === username;
  const type =
    tx.type_transaction === "transfert"
      ? isSender
        ? "envoi"
        : "reception"
      : tx.type_transaction === "paiement"
        ? "paiement"
        : tx.type_transaction;

  return {
    id: String(tx.id_transaction),
    type,
    counterparty: isSender ? tx.destinataire : tx.expediteur,
    amount: Number(tx.montant),
    date: new Date(tx.date_transaction).toLocaleString("fr-FR"),
    status: statusMap[tx.status] ?? "en_attente",
    reference: tx.reference,
  };
};

export const mapMerchantPayment = (payment: MerchantPayment): Transaction => ({
  id: String(payment.id_paiement),
  type: "reception",
  counterparty: payment.client,
  amount: Number(payment.montant),
  date: new Date(payment.date_paiement).toLocaleString("fr-FR"),
  status: "validée",
  reference: payment.reference,
});

export const mapPendingRequest = (item: PendingDeposit | PendingWithdrawal, type: "depot" | "retrait") => ({
  id: type === "depot" ? (item as PendingDeposit).id_depot : (item as PendingWithdrawal).id_retrait,
  ref: `${type === "depot" ? "DEP" : "RET"}-${type === "depot" ? (item as PendingDeposit).id_depot : (item as PendingWithdrawal).id_retrait}`,
  user: item.utilisateur,
  type,
  amount: Number(item.montant),
  date: new Date(item.date_demande).toLocaleString("fr-FR"),
});
