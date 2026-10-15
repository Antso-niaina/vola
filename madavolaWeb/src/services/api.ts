export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export type Role = "client" | "commercant" | "admin";

export interface UserProfile {
  id_utilisateur: number;
  user?: {
    id: number;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  username?: string;
  email?: string;
  telephone: string;
  role?: Role;
  statut_compte: string;
  date_creation?: string;
  nom_boutique?: string;
  adresse?: string;
  qr_code?: string;
  peut_valider_depot?: boolean;
  peut_valider_retrait?: boolean;
  peut_bloquer_utilisateur?: boolean;
}

export interface Wallet {
  id_portefeuille?: number;
  proprietaire?: string;
  telephone?: string;
  solde: string;
  date_creation?: string;
}

export interface ApiTransaction {
  id_transaction: number;
  type_transaction: "transfert" | "paiement" | "depot" | "retrait";
  montant: string;
  expediteur: string;
  destinataire: string;
  reference: string;
  status: "validee" | "en_attente" | "refusee";
  date_transaction: string;
}

export interface PendingDeposit {
  id_depot: number;
  utilisateur: string;
  montant: string;
  admin: string | null;
  status: string;
  date_demande: string;
  date_validation: string | null;
}

export interface PendingWithdrawal {
  id_retrait: number;
  utilisateur: string;
  montant: string;
  admin: string | null;
  status: string;
  date_demande: string;
  date_validation: string | null;
}

export interface MerchantPayment {
  id_paiement: number;
  client: string;
  commercant: string;
  montant: string;
  reference: string;
  date_paiement: string;
}

export interface LoyalClient {
  id_client: number;
  montant_total: number;
  nb_paiements: number;
}

export interface TopMerchant {
  commercant?: string;
  nom_boutique?: string;
  montant_total?: string | number;
  total?: string | number;
  nb_paiements?: number;
}

export interface UserStats {
  total_utilisateurs?: number;
  total_clients?: number;
  total_commercants?: number;
  total_admins?: number;
  nombre_utilisateurs?: number;
  total?: number;
}

export interface TransactionStats {
  total_transactions?: number;
  volume_total?: string | number;
  total_depots?: number;
  total_retraits?: number;
  total_transferts?: number;
  nombre_transactions?: number;
  total?: number;
}

type RequestOptions = RequestInit & { retry?: boolean };

const storage = {
  get access() {
    return localStorage.getItem("access_token");
  },
  get refresh() {
    return localStorage.getItem("refresh_token");
  },
  setTokens(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("madavola_user");
  },
};

const toMessage = async (response: Response) => {
  try {
    const data = await response.json();
    if (data.detail) return data.detail;
    if (data.error) return data.error;
    if (data.non_field_errors?.[0]) return data.non_field_errors[0];
    return Object.values(data).flat().join("\n") || "Erreur API.";
  } catch {
    return "Erreur API.";
  }
};

export const apiFetch = async <T>(path: string, options: RequestOptions = {}): Promise<T> => {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (storage.access) headers.set("Authorization", `Bearer ${storage.access}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 401 && options.retry !== false && storage.refresh) {
    const refreshResponse = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: storage.refresh }),
    });

    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      storage.setTokens(data.access, storage.refresh);
      return apiFetch<T>(path, { ...options, retry: false });
    }

    storage.clear();
  }

  if (!response.ok) {
    throw new Error(await toMessage(response));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
};

const post = <T>(path: string, body?: unknown) =>
  apiFetch<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });

const put = <T>(path: string, body?: unknown) =>
  apiFetch<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined });

export const AuthAPI = {
  inscription: (data: {
    username: string;
    email: string;
    password: string;
    telephone: string;
    role: Role;
    nom_boutique?: string;
  }) => post<{ message: string; username: string; role: Role }>("/auth/inscription/", data),

  connexion: (username: string, password: string) =>
    post<{ message: string; username: string; otp_dev?: string }>("/auth/connexion/", { username, password }),

  verifierOTP: (username: string, code_otp: string) =>
    post<{
      message: string;
      access_token: string;
      refresh_token: string;
      role: Role;
      username: string;
    }>("/auth/verifier-otp/", { username, code_otp }),

  deconnexion: (refresh_token: string) => post("/auth/deconnexion/", { refresh_token }),

  changerMotDePasse: (ancien: string, nouveau: string) =>
    post("/auth/changer-mot-de-passe/", {
      ancien_mot_de_passe: ancien,
      nouveau_mot_de_passe: nouveau,
    }),

  listeUtilisateurs: () => apiFetch<UserProfile[]>("/auth/utilisateurs/"),

  attribuerRoleAdmin: (id_utilisateur: number) =>
    post("/auth/attribuer-admin/", { id_utilisateur }),

  modifierPermissionsAdmin: (data: {
    id_utilisateur: number;
    peut_valider_depot?: boolean;
    peut_valider_retrait?: boolean;
    peut_bloquer_utilisateur?: boolean;
  }) => put("/auth/modifier-permissions-admin/", data),
};

export const CompteAPI = {
  profil: () => apiFetch<UserProfile>("/compte/profil/"),
  updateProfil: (data: Partial<UserProfile> & { first_name?: string; last_name?: string; email?: string }) =>
    put<UserProfile>("/compte/profil/update/", data),
  listeUtilisateurs: () => apiFetch<UserProfile[]>("/compte/utilisateurs/"),
};

export const PortefeuilleAPI = {
  solde: () => apiFetch<Wallet>("/portfeuilles/solde/"),
  transfert: (telephone_destinataire: string, montant: number, note?: string) =>
    post<{ detail: string }>("/portfeuilles/transfert/", { telephone_destinataire, montant, note }),
  topPortefeuilles: (k = 10) => apiFetch<Array<Record<string, unknown>>>(`/portfeuilles/admin/top-portefeuilles/?k=${k}`),
  cyclesSuspects: () => apiFetch<{ cycles_detectes: unknown[]; nb: number }>("/portfeuilles/admin/cycles-suspects/"),
};

export const TransactionAPI = {
  historique: () => apiFetch<ApiTransaction[]>("/transaction/historique/"),
  demandeDepot: (montant: number) => post<{ detail: string }>("/transaction/demande-depot/", { montant }),
  demandeRetrait: (montant: number) => post<{ detail: string }>("/transaction/demande-retrait/", { montant }),
  depotsEnAttente: () => apiFetch<PendingDeposit[]>("/transaction/admin/depots-en-attente/"),
  retraitsEnAttente: () => apiFetch<PendingWithdrawal[]>("/transaction/admin/retraits-en-attente/"),
  validerDepot: (id: number) => post<{ detail: string }>(`/transaction/admin/valider-depot/${id}/`),
  refuserDepot: (id: number) => post<{ detail: string }>(`/transaction/admin/refuser-depot/${id}/`),
  validerRetrait: (id: number) => post<{ detail: string }>(`/transaction/admin/valider-retrait/${id}/`),
  refuserRetrait: (id: number) => post<{ detail: string }>(`/transaction/admin/refuser-retrait/${id}/`),
  topTransactions: (k = 10) => apiFetch<ApiTransaction[]>(`/transaction/admin/top-transactions/?k=${k}`),
  plageMonant: (min: number, max: number) =>
    apiFetch<ApiTransaction[]>(`/transaction/admin/plage-montant/?min=${min}&max=${max}`),
};

export const CommercantAPI = {
  genererQR: () => apiFetch<{ id_qr: number; commercant: string; code_qr: string; date_creation: string }>("/commercants/qr-code/generer/"),
  paiementQR: (code_qr: string, montant: number) =>
    post<MerchantPayment>("/commercants/paiement/", { code_qr, montant }),
  historiquePaiements: () => apiFetch<MerchantPayment[]>("/commercants/historique-paiements/"),
  historiqueRevenus: () => apiFetch<MerchantPayment[]>("/commercants/historique-revenus/"),
  clientsFideles: () => apiFetch<LoyalClient[]>("/commercants/clients-fideles/"),
  topCommercantsLive: (n = 10) =>
    apiFetch<TopMerchant[]>(`/commercants/admin/top-commercants-live/?n=${n}`),
  paiementsPlage: (min: number, max: number) =>
    apiFetch<MerchantPayment[]>(`/commercants/admin/paiements-plage/?min=${min}&max=${max}`),
};

export const StatsAPI = {
  nbrUtilisateurs: () => apiFetch<UserStats | number>("/stats/nombre-utilisateurs/"),
  nbrTransactions: () => apiFetch<TransactionStats | number>("/stats/nombre-transactions/"),
  depotsAttente: () => apiFetch<PendingDeposit[]>("/stats/depots-en-attente/"),
  retraitsAttente: () => apiFetch<PendingWithdrawal[]>("/stats/retraits-en-attente/"),
  metriquesDashboard: (quota = 15) => apiFetch<Record<string, unknown>>(`/stats/metriques-dashboard/?quota=${quota}`),
  transactionsParPeriode: (type_periode: "jour" | "semaine" | "mois") =>
    apiFetch<Array<Record<string, unknown>>>(`/stats/transactions-par-periode/?type_periode=${type_periode}`),
  topCommercants: (k = 10) => apiFetch<TopMerchant[]>(`/stats/top-commercants/?k=${k}`),
  topUtilisateurs: (k = 10) => apiFetch<Array<Record<string, unknown>>>(`/stats/top-utilisateurs/?k=${k}`),
  transactionsSuspectes: (seuil_haut = 1000000, seuil_freq = 20) =>
    apiFetch<Record<string, unknown>>(`/stats/transactions-suspectes/?seuil_haut=${seuil_haut}&seuil_freq=${seuil_freq}`),
  statsRange: (debut: string, fin: string) =>
    apiFetch<Record<string, unknown>>(`/stats/stats-range/?debut=${debut}&fin=${fin}`),
};

export const formatApiError = (error: unknown, fallback = "Une erreur est survenue.") =>
  error instanceof Error && error.message ? error.message : fallback;

export const tokenStorage = storage;
