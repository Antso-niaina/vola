

import heapq
from decimal import Decimal





class PortefeuilleHashTable:

    def __init__(self, capacite: int = 128):
        self._capacite = capacite
        self._buckets: list[list] = [[] for _ in range(capacite)]
        self._taille = 0

    def _hash(self, cle: int) -> int:
        return (cle * 2654435761) % self._capacite

    def inserer(self, id_utilisateur: int, id_portefeuille: int, solde: Decimal) -> None:
        idx = self._hash(id_utilisateur)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == id_utilisateur:
                bucket[i] = (id_utilisateur, {'id_portefeuille': id_portefeuille, 'solde': solde})
                return
        bucket.append((id_utilisateur, {'id_portefeuille': id_portefeuille, 'solde': solde}))
        self._taille += 1

    def obtenir(self, id_utilisateur: int) -> dict | None:
        idx = self._hash(id_utilisateur)
        for k, v in self._buckets[idx]:
            if k == id_utilisateur:
                return v
        return None

    def mettre_a_jour_solde(self, id_utilisateur: int, nouveau_solde: Decimal) -> bool:
        idx = self._hash(id_utilisateur)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == id_utilisateur:
                self._buckets[idx][i] = (k, {**v, 'solde': nouveau_solde})
                return True
        return False

    def supprimer(self, id_utilisateur: int) -> bool:
        idx = self._hash(id_utilisateur)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == id_utilisateur:
                bucket.pop(i)
                self._taille -= 1
                return True
        return False

    def solde(self, id_utilisateur: int) -> Decimal | None:
        info = self.obtenir(id_utilisateur)
        return info['solde'] if info else None

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"PortefeuilleHashTable(taille={self._taille})"





class TransfertHeap:

    def __init__(self):
        self._heap: list[tuple] = []
        self._counter = 0  

    def ajouter(self, montant: Decimal, id_expediteur: int,
                id_destinataire: int, reference: str) -> None:
        
        heapq.heappush(self._heap, (-float(montant), self._counter, id_expediteur, id_destinataire, reference))
        self._counter += 1

    def retirer_prioritaire(self) -> dict | None:
        if self._heap:
            neg_montant, _, exp, dest, ref = heapq.heappop(self._heap)
            return {
                'montant': Decimal(str(-neg_montant)),
                'id_expediteur': exp,
                'id_destinataire': dest,
                'reference': ref,
            }
        return None

    def apercu(self) -> dict | None:
        if self._heap:
            neg_montant, _, exp, dest, ref = self._heap[0]
            return {
                'montant': Decimal(str(-neg_montant)),
                'id_expediteur': exp,
                'id_destinataire': dest,
                'reference': ref,
            }
        return None

    def taille(self) -> int:
        return len(self._heap)

    def __repr__(self):
        return f"TransfertHeap(en_attente={len(self._heap)})"





class GrapheFluxFinanciers:

    def __init__(self):
        self._adj: dict[int, dict[int, float]] = {}

    def ajouter_noeud(self, id_portefeuille: int) -> None:
        if id_portefeuille not in self._adj:
            self._adj[id_portefeuille] = {}

    def enregistrer_transfert(self, source: int, cible: int, montant: float) -> None:
        self.ajouter_noeud(source)
        self.ajouter_noeud(cible)
        self._adj[source][cible] = self._adj[source].get(cible, 0.0) + montant

    def flux_sortant_total(self, id_portefeuille: int) -> float:
        return sum(self._adj.get(id_portefeuille, {}).values())

    def flux_entrant_total(self, id_portefeuille: int) -> float:
        return sum(
            aretes.get(id_portefeuille, 0.0)
            for aretes in self._adj.values()
        )

    def detecter_cycle(self, depart: int) -> bool:
        """DFS pour détecter un cycle depuis un nœud."""
        visites: set[int] = set()
        pile: set[int] = set()

        def dfs(noeud: int) -> bool:
            visites.add(noeud)
            pile.add(noeud)
            for voisin in self._adj.get(noeud, {}):
                if voisin not in visites:
                    if dfs(voisin):
                        return True
                elif voisin in pile:
                    return True
            pile.remove(noeud)
            return False

        return dfs(depart)

    def voisins(self, id_portefeuille: int) -> dict[int, float]:
        return self._adj.get(id_portefeuille, {})

    def nb_noeuds(self) -> int:
        return len(self._adj)

    def __repr__(self):
        nb_aretes = sum(len(v) for v in self._adj.values())
        return f"GrapheFluxFinanciers(portefeuilles={len(self._adj)}, flux={nb_aretes})"





cache_portefeuilles = PortefeuilleHashTable()
file_transferts = TransfertHeap()
graphe_flux = GrapheFluxFinanciers()
