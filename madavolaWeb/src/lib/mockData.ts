
export const currency = (n: number) =>
  new Intl.NumberFormat("fr-MG", { maximumFractionDigits: 0 }).format(n) + " Ar";

export const currentUser = {
  name: "Antsotiana A.",
  phone: "+261 34 12 345 67",
  walletId: "MV-7842-3019",
  balance: 1_245_800,
  initials: "AA",
};

export const currentMerchant = {
  name: "Épicerie Tsara",
  owner: "Rakoto Jean",
  phone: "+261 32 88 776 65",
  walletId: "MVM-1029-4471",
  balance: 4_820_300,
  todaySales: 685_000,
  initials: "ÉT",
};

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

export const userTransactions: Transaction[] = [
  { id: "T-10293", type: "reception", counterparty: "Hery R.", amount: 120_000, date: "2026-04-22 09:14", status: "validée", reference: "REF-AX91" },
  { id: "T-10288", type: "paiement", counterparty: "Épicerie Tsara", amount: 45_500, date: "2026-04-21 18:42", status: "validée", reference: "REF-PQ22" },
  { id: "T-10277", type: "envoi", counterparty: "Mialy V.", amount: 80_000, date: "2026-04-20 11:03", status: "validée", reference: "REF-LM18" },
  { id: "T-10260", type: "depot", counterparty: "Admin MadaVola", amount: 500_000, date: "2026-04-18 14:20", status: "validée", reference: "REF-DP04" },
  { id: "T-10254", type: "paiement", counterparty: "Resto Soa", amount: 32_000, date: "2026-04-17 12:55", status: "validée", reference: "REF-RS09" },
  { id: "T-10231", type: "retrait", counterparty: "Admin MadaVola", amount: 200_000, date: "2026-04-15 10:11", status: "en_attente", reference: "REF-RT77" },
  { id: "T-10220", type: "envoi", counterparty: "Tahina F.", amount: 25_000, date: "2026-04-14 17:30", status: "validée", reference: "REF-TF12" },
  { id: "T-10199", type: "reception", counterparty: "Naina B.", amount: 60_000, date: "2026-04-12 08:48", status: "validée", reference: "REF-NB55" },
];

export const merchantSales: Transaction[] = [
  { id: "S-55401", type: "reception", counterparty: "Antsotiana A.", amount: 45_500, date: "2026-04-22 18:42", status: "validée", reference: "REF-PQ22" },
  { id: "S-55389", type: "reception", counterparty: "Mialy V.", amount: 18_000, date: "2026-04-22 17:15", status: "validée", reference: "REF-MV01" },
  { id: "S-55372", type: "reception", counterparty: "Hery R.", amount: 92_000, date: "2026-04-22 14:03", status: "validée", reference: "REF-HR88" },
  { id: "S-55360", type: "reception", counterparty: "Naina B.", amount: 27_500, date: "2026-04-22 11:21", status: "validée", reference: "REF-NB12" },
  { id: "S-55321", type: "reception", counterparty: "Tahina F.", amount: 154_000, date: "2026-04-21 19:30", status: "validée", reference: "REF-TF44" },
  { id: "S-55310", type: "reception", counterparty: "Sarah M.", amount: 38_000, date: "2026-04-21 16:48", status: "validée", reference: "REF-SM21" },
];

export const adminPendingRequests = [
  { id: "DEP-3401", user: "Mialy Voahangy", phone: "+261 33 11 222 33", type: "depot" as const, amount: 750_000, date: "2026-04-22 10:14" },
  { id: "RET-2210", user: "Antsotiana A.", phone: "+261 34 12 345 67", type: "retrait" as const, amount: 200_000, date: "2026-04-22 09:42" },
  { id: "DEP-3402", user: "Hery Rajao", phone: "+261 32 99 888 77", type: "depot" as const, amount: 1_200_000, date: "2026-04-22 09:18" },
  { id: "RET-2211", user: "Épicerie Tsara", phone: "+261 32 88 776 65", type: "retrait" as const, amount: 850_000, date: "2026-04-22 08:55" },
  { id: "DEP-3403", user: "Naina Be", phone: "+261 34 55 666 77", type: "depot" as const, amount: 300_000, date: "2026-04-21 17:30" },
];

export const adminUsers = [
  { id: "U-1001", name: "Antsotiana A.", phone: "+261 34 12 345 67", role: "Client", status: "Actif", balance: 1_245_800, joined: "2025-09-12" },
  { id: "U-1002", name: "Mialy Voahangy", phone: "+261 33 11 222 33", role: "Client", status: "Actif", balance: 540_000, joined: "2025-10-04" },
  { id: "U-1003", name: "Épicerie Tsara", phone: "+261 32 88 776 65", role: "Commerçant", status: "Actif", balance: 4_820_300, joined: "2025-08-20" },
  { id: "U-1004", name: "Hery Rajao", phone: "+261 32 99 888 77", role: "Client", status: "Suspendu", balance: 12_000, joined: "2025-11-01" },
  { id: "U-1005", name: "Resto Soa", phone: "+261 34 77 555 11", role: "Commerçant", status: "Actif", balance: 2_180_500, joined: "2025-07-18" },
  { id: "U-1006", name: "Naina Be", phone: "+261 34 55 666 77", role: "Client", status: "Actif", balance: 320_000, joined: "2026-01-09" },
  { id: "U-1007", name: "Tahina Fano", phone: "+261 33 22 444 99", role: "Client", status: "Actif", balance: 88_500, joined: "2026-02-14" },
];

export const adminStats = {
  totalUsers: 12_487,
  totalMerchants: 842,
  totalVolume: 1_284_500_000,
  todayTransactions: 3_412,
};

export const volumeChartData = [
  { day: "Lun", volume: 120, transactions: 280 },
  { day: "Mar", volume: 145, transactions: 312 },
  { day: "Mer", volume: 132, transactions: 298 },
  { day: "Jeu", volume: 178, transactions: 365 },
  { day: "Ven", volume: 215, transactions: 412 },
  { day: "Sam", volume: 248, transactions: 488 },
  { day: "Dim", volume: 192, transactions: 378 },
];

export const userVolumeData = [
  { day: "L", in: 120, out: 45 },
  { day: "M", in: 80, out: 60 },
  { day: "M", in: 200, out: 120 },
  { day: "J", in: 150, out: 90 },
  { day: "V", in: 90, out: 110 },
  { day: "S", in: 60, out: 80 },
  { day: "D", in: 180, out: 50 },
];

export const merchantSalesChart = [
  { day: "Lun", sales: 320 },
  { day: "Mar", sales: 410 },
  { day: "Mer", sales: 380 },
  { day: "Jeu", sales: 520 },
  { day: "Ven", sales: 685 },
  { day: "Sam", sales: 740 },
  { day: "Dim", sales: 460 },
];

export const contacts = [
  { id: "C1", name: "Mialy V.", phone: "+261 33 11 222 33", initials: "MV" },
  { id: "C2", name: "Hery R.", phone: "+261 32 99 888 77", initials: "HR" },
  { id: "C3", name: "Naina B.", phone: "+261 34 55 666 77", initials: "NB" },
  { id: "C4", name: "Tahina F.", phone: "+261 33 22 444 99", initials: "TF" },
  { id: "C5", name: "Sarah M.", phone: "+261 34 88 110 22", initials: "SM" },
];
