import { useState } from "react";
import { Download, Filter, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TransactionList } from "@/components/TransactionList";
import { TransactionAPI } from "@/services/api";
import { mapTransaction } from "@/lib/apiMappers";
import { useAuthStore } from "@/hooks/useAuthStore";
import { useQuery } from "@tanstack/react-query";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

const filters = ["Toutes", "Envoi", "Réception", "Paiement", "Dépôt", "Retrait"] as const;

const History = () => {
  const [active, setActive] = useState<(typeof filters)[number]>("Toutes");
  const { user } = useAuthStore();
  const { data = [], isLoading } = useQuery({ queryKey: ["transactions"], queryFn: TransactionAPI.historique });
  const transactions = data.map((tx) => mapTransaction(tx, user?.username));

  const filtered = transactions.filter((t) => {
    if (active === "Toutes") return true;
    const map: Record<string, string> = {
      Envoi: "envoi",
      Réception: "reception",
      Paiement: "paiement",
      Dépôt: "depot",
      Retrait: "retrait",
    };
    return t.type === map[active];
  });

  const handleExportPDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(16);
    doc.text("Historique des transactions", 14, 20);

    doc.setFontSize(10);
    doc.setTextColor(120);
    doc.text(`Filtre : ${active}`, 14, 28);
    doc.text(`Exporté le : ${new Date().toLocaleDateString("fr-FR")}`, 14, 34);

    autoTable(doc, {
      startY: 42,
      head: [["Date", "Type", "Destinataire / Libellé", "Montant"]],
      body: filtered.map((t) => [
        new Date(t.date).toLocaleDateString("fr-FR"),
        t.type,
        t.counterparty ?? "-",
        `${t.amount} Ar`,
      ]),
      styles: { fontSize: 9 },
      headStyles: { fillColor: [30, 30, 30] },
    });

    doc.save("historique-transactions.pdf");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">Historique</h1>
          <p className="mt-1 text-sm text-muted-foreground">Toutes vos transactions, filtrables et exportables.</p>
        </div>
        <Button variant="outline" onClick={handleExportPDF}>
          <Download className="h-4 w-4" />
          Exporter PDF
        </Button>
      </div>

      <div className="rounded-2xl border border-border bg-card p-5 shadow-card-soft">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input className="pl-9" placeholder="Rechercher par nom, référence..." />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4" />
            Filtres avancés
          </Button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActive(f)}
              className={`rounded-full px-4 py-1.5 text-xs font-semibold transition-smooth ${
                active === f
                  ? "bg-primary text-primary-foreground shadow-card-soft"
                  : "bg-muted/60 text-muted-foreground hover:bg-muted"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="mt-4">
          <TransactionList transactions={filtered} />
          {(filtered.length === 0 || isLoading) && (
            <p className="py-12 text-center text-sm text-muted-foreground">
              {isLoading ? "Chargement de l'historique..." : "Aucune transaction pour ce filtre."}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default History;