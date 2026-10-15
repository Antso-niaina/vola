import { useState } from "react";
import { Download, Search } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TransactionList } from "@/components/TransactionList";
import { CommercantAPI } from "@/services/api";
import { mapMerchantPayment, Transaction } from "@/lib/apiMappers";

const MerchantSales = () => {
  const [search, setSearch] = useState("");
  const [period, setPeriod] = useState("Tout");

  const { data = [], isLoading } = useQuery({
    queryKey: ["merchant-revenues"],
    queryFn: CommercantAPI.historiqueRevenus,
  });

  const sales = data.map(mapMerchantPayment);

  const filterByPeriod = (sale: Transaction) => {
    const now = new Date();
    const [datePart] = sale.date.split(" ");
    const [day, month, year] = datePart.split("/");
    const saleDate = new Date(`${year}-${month}-${day}`);

    if (period === "Aujourd'hui") {
      return saleDate.toDateString() === now.toDateString();
    }
    if (period === "7 derniers jours") {
      return (now.getTime() - saleDate.getTime()) / 86400000 <= 7;
    }
    if (period === "30 derniers jours") {
      return (now.getTime() - saleDate.getTime()) / 86400000 <= 30;
    }
    return true;
  };

  const filteredSales = sales.filter((sale) => {
    const matchesPeriod = filterByPeriod(sale);
    const query = search.toLowerCase();
    const matchesSearch =
      !query ||
      sale.reference?.toLowerCase().includes(query) ||
      sale.counterparty?.toLowerCase().includes(query);
    return matchesPeriod && matchesSearch;
  });

  const handleExportPDF = () => {
    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Historique des ventes", 14, 20);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(120);
    doc.text(`Exporté le ${new Date().toLocaleDateString("fr-FR")}`, 14, 28);
    doc.text(`Période : ${period}`, 14, 34);
    doc.text(`${filteredSales.length} transaction(s)`, 14, 40);
    doc.setTextColor(0);

    autoTable(doc, {
      startY: 48,
      head: [["Référence", "Client", "Montant", "Date", "Statut"]],
      body: filteredSales.map((s) => [
        s.reference ?? "-",
        s.counterparty ?? "-",
        `${s.amount?.toLocaleString("fr-FR")} Ar`,
        s.date,
        s.status ?? "-",
      ]),
      styles: { fontSize: 9, cellPadding: 4 },
      headStyles: { fillColor: [37, 99, 235], fontStyle: "bold" },
      alternateRowStyles: { fillColor: [245, 247, 255] },
      columnStyles: {
        2: { halign: "right" },
      },
    });

    doc.save(`ventes_${new Date().toISOString().slice(0, 10)}.pdf`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
            Mes ventes
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Historique de tous les paiements reçus.
          </p>
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
            <Input
              className="pl-9"
              placeholder="Rechercher un client, une référence..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            className="rounded-lg border border-input bg-background px-3 py-2 text-sm"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option>Aujourd'hui</option>
            <option>7 derniers jours</option>
            <option>30 derniers jours</option>
            <option>Tout</option>
          </select>
        </div>

        <div className="mt-4">
          {isLoading ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Chargement...
            </p>
          ) : filteredSales.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Aucune vente pour l'instant.
            </p>
          ) : (
            <TransactionList transactions={filteredSales} perspective="merchant" />
          )}
        </div>
      </div>
    </div>
  );
};

export default MerchantSales;