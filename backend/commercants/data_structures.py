

import heapq
from decimal import Decimal
from datetime import datetime





class QRCodeHashTable:

    def __init__(self, capacite: int = 256):
        self._capacite = capacite
        self._buckets: list[list] = [[] for _ in range(capacite)]
        self._taille = 0

    def _hash(self, code: str) -> int:
        h = 14695981039346656037
        for c in code:
            h ^= ord(c)
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        return h % self._capacite

    def inserer(self, code_qr: str, id_commercant: int,
                nom_boutique: str, actif: bool = True) -> None:
        idx = self._hash(code_qr)
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == code_qr:
                self._buckets[idx][i] = (code_qr, {
                    'id_commercant': id_commercant,
                    'nom_boutique': nom_boutique,
                    'actif': actif,
                })
                return
        self._buckets[idx].append((code_qr, {
            'id_commercant': id_commercant,
            'nom_boutique': nom_boutique,
            'actif': actif,
        }))
        self._taille += 1

    def obtenir(self, code_qr: str) -> dict | None:
        idx = self._hash(code_qr)
        for k, v in self._buckets[idx]:
            if k == code_qr:
                return v
        return None

    def desactiver(self, code_qr: str) -> bool:
        idx = self._hash(code_qr)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == code_qr:
                self._buckets[idx][i] = (k, {**v, 'actif': False})
                return True
        return False

    def est_actif(self, code_qr: str) -> bool:
        info = self.obtenir(code_qr)
        return bool(info and info.get('actif', False))

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"QRCodeHashTable(taille={self._taille})"





class ClassementCommercantHeap:

    def __init__(self):
        
        self._heap: list[tuple] = []
        
        self._index: dict[int, dict] = {}

    def ajouter_ou_mettre_a_jour(self, id_commercant: int,
                                  nom_boutique: str, montant: float) -> None:
        if id_commercant in self._index:
            self._index[id_commercant]['ca'] += montant
        else:
            self._index[id_commercant] = {'nom': nom_boutique, 'ca': montant}
            heapq.heappush(self._heap,
                           (-montant, id_commercant, nom_boutique))

        
        ca = self._index[id_commercant]['ca']
        heapq.heappush(self._heap, (-ca, id_commercant, nom_boutique))

    def top_n(self, n: int = 10) -> list[dict]:
        
        vus: set[int] = set()
        resultat = []
        temp = list(self._heap)
        heapq.heapify(temp)

        while temp and len(resultat) < n:
            neg_ca, cid, nom = heapq.heappop(temp)
            if cid in vus:
                continue
            vus.add(cid)
            ca_reel = self._index.get(cid, {}).get('ca', -neg_ca)
            resultat.append({'id_commercant': cid, 'nom_boutique': nom, 'ca_total': ca_reel})

        return resultat

    def ca_de(self, id_commercant: int) -> float:
        return self._index.get(id_commercant, {}).get('ca', 0.0)

    def nb_commercants(self) -> int:
        return len(self._index)

    def __repr__(self):
        return f"ClassementCommercantHeap(commerçants={len(self._index)})"





class GraphePaiements:
    def __init__(self):
        
        self._adj: dict[int, dict[int, dict]] = {}

    def enregistrer_paiement(self, id_client: int, id_commercant: int,
                              montant: float) -> None:
        if id_client not in self._adj:
            self._adj[id_client] = {}
        if id_commercant not in self._adj[id_client]:
            self._adj[id_client][id_commercant] = {'montant': 0.0, 'nb': 0}
        self._adj[id_client][id_commercant]['montant'] += montant
        self._adj[id_client][id_commercant]['nb'] += 1

    def commercants_du_client(self, id_client: int) -> dict[int, dict]:
        return self._adj.get(id_client, {})

    def clients_du_commercant(self, id_commercant: int) -> list[int]:
        return [cid for cid, coms in self._adj.items() if id_commercant in coms]

    def montant_total_client_commercant(self, id_client: int, id_commercant: int) -> float:
        return self._adj.get(id_client, {}).get(id_commercant, {}).get('montant', 0.0)

    def commercant_prefere(self, id_client: int) -> int | None:
        coms = self._adj.get(id_client, {})
        if not coms:
            return None
        return max(coms, key=lambda c: coms[c]['nb'])

    def nb_clients_uniques(self, id_commercant: int) -> int:
        return len(self.clients_du_commercant(id_commercant))

    def __repr__(self):
        nb_aretes = sum(len(v) for v in self._adj.values())
        return f"GraphePaiements(clients={len(self._adj)}, paiements={nb_aretes})"





class NoeudAVLPaiement:
    __slots__ = ('montant', 'ids', 'hauteur', 'gauche', 'droit')

    def __init__(self, montant: float, id_paiement: int):
        self.montant = montant
        self.ids: list[int] = [id_paiement]
        self.hauteur = 1
        self.gauche = None
        self.droit = None


class AVLPaiements:

    def __init__(self):
        self._racine = None

    @staticmethod
    def _h(n) -> int:
        return n.hauteur if n else 0

    def _fb(self, n) -> int:
        return self._h(n.gauche) - self._h(n.droit)

    def _uh(self, n):
        n.hauteur = 1 + max(self._h(n.gauche), self._h(n.droit))

    def _rd(self, z):
        y = z.gauche; T3 = y.droit
        y.droit = z; z.gauche = T3
        self._uh(z); self._uh(y); return y

    def _rg(self, z):
        y = z.droit; T2 = y.gauche
        y.gauche = z; z.droit = T2
        self._uh(z); self._uh(y); return y

    def _eq(self, n):
        self._uh(n); fb = self._fb(n)
        if fb > 1:
            if self._fb(n.gauche) < 0: n.gauche = self._rg(n.gauche)
            return self._rd(n)
        if fb < -1:
            if self._fb(n.droit) > 0: n.droit = self._rd(n.droit)
            return self._rg(n)
        return n

    def _ins(self, noeud, montant: float, id_paiement: int):
        if not noeud:
            return NoeudAVLPaiement(montant, id_paiement)
        if montant < noeud.montant:
            noeud.gauche = self._ins(noeud.gauche, montant, id_paiement)
        elif montant > noeud.montant:
            noeud.droit = self._ins(noeud.droit, montant, id_paiement)
        else:
            noeud.ids.append(id_paiement)
            return noeud
        return self._eq(noeud)

    def inserer(self, montant: float, id_paiement: int) -> None:
        self._racine = self._ins(self._racine, montant, id_paiement)

    def _range(self, noeud, min_m: float, max_m: float, res: list):
        if not noeud:
            return
        if noeud.montant > min_m:
            self._range(noeud.gauche, min_m, max_m, res)
        if min_m <= noeud.montant <= max_m:
            res.extend(noeud.ids)
        if noeud.montant < max_m:
            self._range(noeud.droit, min_m, max_m, res)

    def paiements_dans_plage(self, min_montant: float, max_montant: float) -> list[int]:
        res: list[int] = []
        self._range(self._racine, min_montant, max_montant, res)
        return res

    def __repr__(self):
        return f"AVLPaiements(hauteur={self._h(self._racine)})"





index_qrcodes = QRCodeHashTable()
classement_commercants = ClassementCommercantHeap()
graphe_paiements = GraphePaiements()
avl_paiements = AVLPaiements()
