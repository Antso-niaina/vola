import { useState } from "react";
import { Loader2, MoreHorizontal, Search, ShieldCheck, UserPlus } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { AuthAPI, formatApiError, UserProfile } from "@/services/api";
import { displayName, initials } from "@/lib/apiMappers";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const AdminUsers = () => {
  const [query, setQuery] = useState("");
  const queryClient = useQueryClient();
  const { data: users = [], isLoading } = useQuery({ queryKey: ["admin-users"], queryFn: AuthAPI.listeUtilisateurs });
  const { mutate: promoteToAdmin, isPending } = useMutation({
    mutationFn: (id_utilisateur: number) => AuthAPI.attribuerRoleAdmin(id_utilisateur),
    onSuccess: async () => {
      toast.success("Rôle admin attribué", { description: "La liste des utilisateurs a été mise à jour." });
      await queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: (error) => {
      toast.error("Attribution impossible", { description: formatApiError(error) });
    },
  });

  const handlePromoteToAdmin = (user: UserProfile) => {
    const name = displayName(user);
    const confirmed = window.confirm(`Attribuer le rôle administrateur à ${name} ?`);
    if (confirmed) promoteToAdmin(user.id_utilisateur);
  };

  const filtered = users.filter(
    (u) =>
      displayName(u).toLowerCase().includes(query.toLowerCase()) ||
      (u.telephone ?? "").includes(query) ||
      String(u.id_utilisateur).includes(query)
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Utilisateurs</h1>
          <p className="mt-1 text-sm text-muted-foreground">Gérez les comptes clients et commerçants.</p>
        </div>
        <Button className="bg-gradient-primary">
          <UserPlus className="h-4 w-4" />
          Inviter un utilisateur
        </Button>
      </div>

      <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
        <div className="relative max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input className="pl-9" placeholder="Rechercher par nom, ID ou téléphone..." value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[800px]">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <th className="pb-3">Utilisateur</th>
                <th className="pb-3">Téléphone</th>
                <th className="pb-3">Rôle</th>
                <th className="pb-3">Statut</th>
                <th className="pb-3 text-right">Solde</th>
                <th className="pb-3">Inscrit le</th>
                <th className="pb-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading && (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-sm text-muted-foreground">Chargement...</td>
                </tr>
              )}
              {!isLoading && filtered.map((u) => {
                const name = displayName(u);
                return (
                  <tr key={u.id_utilisateur} className="text-sm transition-smooth hover:bg-muted/30">
                    <td className="py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-primary text-xs font-bold text-primary-foreground">
                          {initials(name)}
                        </div>
                        <div>
                          <p className="font-semibold">{name}</p>
                          <p className="font-mono text-xs text-muted-foreground">U-{u.id_utilisateur}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 text-muted-foreground">{u.telephone}</td>
                    <td className="py-3">
                      <span
                        className={cn(
                          "rounded-full px-2.5 py-0.5 text-xs font-semibold",
                          u.role === "commercant" ? "bg-gold/15 text-gold-foreground" : "bg-primary/10 text-primary"
                        )}
                        style={u.role === "commercant" ? { color: "hsl(var(--gold))" } : undefined}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold",
                          u.statut_compte === "actif" ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
                        )}
                      >
                        <span className={cn("h-1.5 w-1.5 rounded-full", u.statut_compte === "actif" ? "bg-success" : "bg-destructive")} />
                        {u.statut_compte}
                      </span>
                    </td>
                    <td className="py-3 text-right font-display font-bold">—</td>
                    <td className="py-3 text-muted-foreground">{u.date_creation ? new Date(u.date_creation).toLocaleDateString("fr-FR") : "—"}</td>
                    <td className="py-3 text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" disabled={isPending}>
                            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <MoreHorizontal className="h-4 w-4" />}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            disabled={u.role === "admin" || isPending}
                            onClick={() => handlePromoteToAdmin(u)}
                          >
                            <ShieldCheck className="mr-2 h-4 w-4" />
                            Attribuer rôle admin
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminUsers;
