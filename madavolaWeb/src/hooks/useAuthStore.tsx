import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { CompteAPI, Role, tokenStorage, UserProfile } from "@/services/api";

interface AuthUser {
  id_utilisateur: number;
  username: string;
  email: string;
  telephone: string;
  role: Role;
  statut_compte: string;
  nom_boutique?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  pendingUsername: string | null;
  isLoading: boolean;
  setPendingUsername: (username: string | null) => void;
  setSession: (access: string, refresh: string, role: Role, username: string) => Promise<AuthUser>;
  refreshProfile: () => Promise<AuthUser | null>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const roleFromProfile = (profile: UserProfile, fallback?: Role): Role => {
  if (profile.role) return profile.role;
  if (
    profile.peut_valider_depot !== undefined ||
    profile.peut_valider_retrait !== undefined ||
    profile.peut_bloquer_utilisateur !== undefined
  ) {
    return "admin";
  }
  if (profile.nom_boutique !== undefined || profile.adresse !== undefined || profile.qr_code !== undefined) {
    return "commercant";
  }
  return fallback ?? "client";
};

const userFromProfile = (profile: UserProfile, fallback?: { role?: Role; username?: string }): AuthUser => ({
  id_utilisateur: profile.id_utilisateur ?? 0,
  username: profile.user?.username ?? fallback?.username ?? "",
  email: profile.user?.email ?? "",
  telephone: profile.telephone ?? "",
  role: roleFromProfile(profile, fallback?.role),
  statut_compte: profile.statut_compte ?? "actif",
  nom_boutique: profile.nom_boutique,
});

const saveUser = (user: AuthUser | null) => {
  if (user) localStorage.setItem("madavola_user", JSON.stringify(user));
  else localStorage.removeItem("madavola_user");
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [pendingUsername, setPendingUsername] = useState<string | null>(() => sessionStorage.getItem("pending_username"));
  const [isLoading, setIsLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    if (!tokenStorage.access) {
      setUser(null);
      saveUser(null);
      return null;
    }

    const profile = await CompteAPI.profil();
    const nextUser = userFromProfile(profile, user ?? undefined);
    setUser(nextUser);
    saveUser(nextUser);
    return nextUser;
  }, [user]);

  useEffect(() => {
    const saved = localStorage.getItem("madavola_user");
    if (saved) setUser(JSON.parse(saved));

    refreshProfile()
      .catch(() => {
        tokenStorage.clear();
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    if (pendingUsername) sessionStorage.setItem("pending_username", pendingUsername);
    else sessionStorage.removeItem("pending_username");
  }, [pendingUsername]);

  const setSession = useCallback(async (access: string, refresh: string, role: Role, username: string) => {
    tokenStorage.setTokens(access, refresh);
    const profile = await CompteAPI.profil().catch(() => null);
    const nextUser = profile
      ? userFromProfile(profile, { role, username })
      : { id_utilisateur: 0, username, email: "", telephone: "", role, statut_compte: "actif" };

    setUser(nextUser);
    saveUser(nextUser);
    setPendingUsername(null);
    return nextUser;
  }, []);

  const logout = useCallback(() => {
    tokenStorage.clear();
    saveUser(null);
    setUser(null);
    setPendingUsername(null);
  }, []);

  const value = useMemo(
    () => ({ user, pendingUsername, isLoading, setPendingUsername, setSession, refreshProfile, logout }),
    [user, pendingUsername, isLoading, setSession, refreshProfile, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthStore = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuthStore must be used inside AuthProvider");
  return context;
};
