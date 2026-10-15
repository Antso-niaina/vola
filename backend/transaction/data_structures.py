

import heapq
from decimal import Decimal
from datetime import datetime





class TransactionHashTable:

    def __init__(self, capacite: int = 512):
        self._capacite = capacite
        self._buckets: list[list] = [[] for _ in range(capacite)]
        self._taille = 0

    def _hash(self, reference: str) -> int:
        h = 0
        for i, c in enumerate(reference):
            h = (h * 37 + ord(c) * (i + 1)) % self._capacite
        return h

    def inserer(self, reference: str, transaction: dict) -> None:
        idx = self._hash(reference)
        for i, (r, _) in enumerate(self._buckets[idx]):
            if r == reference:
                self._buckets[idx][i] = (reference, transaction)
                return
        self._buckets[idx].append((reference, transaction))
        self._taille += 1

    def obtenir(self, reference: str) -> dict | None:
        idx = self._hash(reference)
        for r, t in self._buckets[idx]:
            if r == reference:
                return t
        return None

    def supprimer(self, reference: str) -> bool:
        idx = self._hash(reference)
        bucket = self._buckets[idx]
        for i, (r, _) in enumerate(bucket):
            if r == reference:
                bucket.pop(i)
                self._taille -= 1
                return True
        return False

    def existe(self, reference: str) -> bool:
        return self.obtenir(reference) is not None

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"TransactionHashTable(taille={self._taille}, capacite={self._capacite})"





class DemandeAdminHeap:

    def __init__(self):
        self._heap: list[tuple] = []
        self._counter = 0

    def ajouter_depot(self, id_depot: int, id_utilisateur: int,montant: Decimal, date_demande: datetime) -> None:
        ts = date_demande.timestamp()
        heapq.heappush(self._heap,
                       (ts, self._counter, 'depot', id_depot, id_utilisateur, float(montant)))
        self._counter += 1

    def ajouter_retrait(self, id_retrait: int, id_utilisateur: int,
                        montant: Decimal, date_demande: datetime) -> None:
        ts = date_demande.timestamp()
        heapq.heappush(self._heap,
                       (ts, self._counter, 'retrait', id_retrait, id_utilisateur, float(montant)))
        self._counter += 1

    def retirer_prioritaire(self) -> dict | None:
        if self._heap:
            ts, _, type_op, id_op, id_util, montant = heapq.heappop(self._heap)
            return {
                'type': type_op,
                'id': id_op,
                'id_utilisateur': id_util,
                'montant': Decimal(str(montant)),
                'date_demande': datetime.fromtimestamp(ts),
            }
        return None

    def apercu(self) -> dict | None:
        if self._heap:
            ts, _, type_op, id_op, id_util, montant = self._heap[0]
            return {
                'type': type_op,
                'id': id_op,
                'id_utilisateur': id_util,
                'montant': Decimal(str(montant)),
                'date_demande': datetime.fromtimestamp(ts),
            }
        return None

    def taille(self) -> int:
        return len(self._heap)

    def nb_par_type(self) -> dict[str, int]:
        compteur = {'depot': 0, 'retrait': 0}
        for item in self._heap:
            compteur[item[2]] = compteur.get(item[2], 0) + 1
        return compteur

    def __repr__(self):
        return f"DemandeAdminHeap(en_attente={len(self._heap)})"





class GrapheTransactions:

    def __init__(self):
        self._adj: dict[int, dict[int, dict]] = {}

    def ajouter_noeud(self, id_utilisateur: int) -> None:
        if id_utilisateur not in self._adj:
            self._adj[id_utilisateur] = {}

    def enregistrer_transaction(self, expediteur: int, destinataire: int,
                                montant: float, type_transaction: str) -> None:
        self.ajouter_noeud(expediteur)
        self.ajouter_noeud(destinataire)
        if destinataire not in self._adj[expediteur]:
            self._adj[expediteur][destinataire] = {'montant_total': 0.0, 'nb': 0, 'types': set()}
        self._adj[expediteur][destinataire]['montant_total'] += montant
        self._adj[expediteur][destinataire]['nb'] += 1
        self._adj[expediteur][destinataire]['types'].add(type_transaction)

    def flux_entre(self, expediteur: int, destinataire: int) -> dict | None:
        return self._adj.get(expediteur, {}).get(destinataire)

    def expediteurs_vers(self, destinataire: int) -> list[int]:
        """Retourne tous les nœuds qui envoient vers `destinataire`."""
        return [uid for uid, voisins in self._adj.items() if destinataire in voisins]

    def destinataires_de(self, expediteur: int) -> dict[int, dict]:
        return self._adj.get(expediteur, {})

    def volume_sortant(self, expediteur: int) -> float:
        return sum(v['montant_total'] for v in self._adj.get(expediteur, {}).values())

    def volume_entrant(self, destinataire: int) -> float:
        return sum(
            voisins[destinataire]['montant_total']
            for voisins in self._adj.values()
            if destinataire in voisins
        )

    def noeuds_centraux(self, top_n: int = 5) -> list[tuple[int, float]]:
        """Retourne les nœuds avec le plus grand volume sortant."""
        scores = [(uid, self.volume_sortant(uid)) for uid in self._adj]
        return sorted(scores, key=lambda x: -x[1])[:top_n]

    def nb_noeuds(self) -> int:
        return len(self._adj)

    def __repr__(self):
        nb_aretes = sum(len(v) for v in self._adj.values())
        return f"GrapheTransactions(noeuds={len(self._adj)}, arêtes={nb_aretes})"





class NoeudAVLTransaction:
    __slots__ = ('montant', 'transactions', 'hauteur', 'gauche', 'droit')

    def __init__(self, montant: float, transaction_id: int):
        self.montant = montant
        self.transactions: list[int] = [transaction_id]
        self.hauteur = 1
        self.gauche: 'NoeudAVLTransaction | None' = None
        self.droit: 'NoeudAVLTransaction | None' = None


class AVLTransactions:

    def __init__(self):
        self._racine: NoeudAVLTransaction | None = None

    @staticmethod
    def _h(n) -> int:
        return n.hauteur if n else 0

    def _fb(self, n) -> int:
        return self._h(n.gauche) - self._h(n.droit)

    def _uh(self, n) -> None:
        n.hauteur = 1 + max(self._h(n.gauche), self._h(n.droit))

    def _rd(self, z):
        y = z.gauche; T3 = y.droit
        y.droit = z; z.gauche = T3
        self._uh(z); self._uh(y); return y

    def _rg(self, z):
        y = z.droit; T2 = y.gauche
        y.gauche = z; z.droit = T2
        self._uh(z); self._uh(y); return y

    def _equilibrer(self, n):
        self._uh(n); fb = self._fb(n)
        if fb > 1:
            if self._fb(n.gauche) < 0: n.gauche = self._rg(n.gauche)
            return self._rd(n)
        if fb < -1:
            if self._fb(n.droit) > 0: n.droit = self._rd(n.droit)
            return self._rg(n)
        return n

    def _inserer(self, noeud, montant: float, transaction_id: int):
        if not noeud:
            return NoeudAVLTransaction(montant, transaction_id)
        if montant < noeud.montant:
            noeud.gauche = self._inserer(noeud.gauche, montant, transaction_id)
        elif montant > noeud.montant:
            noeud.droit = self._inserer(noeud.droit, montant, transaction_id)
        else:
            noeud.transactions.append(transaction_id)
            return noeud
        return self._equilibrer(noeud)

    def inserer(self, montant: float, transaction_id: int) -> None:
        self._racine = self._inserer(self._racine, montant, transaction_id)

    def _range(self, noeud, min_m: float, max_m: float, resultat: list) -> None:
        if not noeud:
            return
        if noeud.montant > min_m:
            self._range(noeud.gauche, min_m, max_m, resultat)
        if min_m <= noeud.montant <= max_m:
            resultat.extend(noeud.transactions)
        if noeud.montant < max_m:
            self._range(noeud.droit, min_m, max_m, resultat)

    def transactions_dans_plage(self, min_montant: float, max_montant: float) -> list[int]:
        """Retourne les ids des transactions dont le montant est dans [min, max]."""
        resultat: list[int] = []
        self._range(self._racine, min_montant, max_montant, resultat)
        return resultat

    def __repr__(self):
        return f"AVLTransactions(hauteur={self._h(self._racine)})"





index_references = TransactionHashTable()
file_admin = DemandeAdminHeap()
graphe_transactions = GrapheTransactions()
avl_montants = AVLTransactions()
