

import heapq
from datetime import datetime





class UtilisateurHashTable:

    _VIDE = object()
    _SUPPRIME = object()

    def __init__(self, capacite: int = 256):
        self._capacite = capacite
        self._table: list = [self._VIDE] * capacite
        self._taille = 0

    def _hash(self, cle: str) -> int:
        h = 5381
        for c in cle:
            h = ((h << 5) + h + ord(c)) & 0xFFFFFFFF
        return h % self._capacite

    def _sonde(self, cle: str, pour_insertion=False):
        idx = self._hash(cle)
        premiere_suppression = None
        for i in range(self._capacite):
            pos = (idx + i) % self._capacite
            cellule = self._table[pos]
            if cellule is self._VIDE:
                if pour_insertion:
                    return premiere_suppression if premiere_suppression is not None else pos
                return -1
            if cellule is self._SUPPRIME:
                if premiere_suppression is None:
                    premiere_suppression = pos
            elif cellule[0] == cle:
                return pos
        return premiere_suppression if pour_insertion else -1

    def inserer(self, telephone: str, id_utilisateur: int, role: str, username: str) -> None:
        if self._taille / self._capacite > 0.7:
            self._redimensionner()
        pos = self._sonde(telephone, pour_insertion=True)
        if pos >= 0:
            self._table[pos] = (telephone, {'id': id_utilisateur, 'role': role, 'username': username})
            self._taille += 1

    def obtenir(self, telephone: str) -> dict | None:
        pos = self._sonde(telephone)
        if pos >= 0 and self._table[pos] not in (self._VIDE, self._SUPPRIME):
            return self._table[pos][1]
        return None

    def supprimer(self, telephone: str) -> bool:
        pos = self._sonde(telephone)
        if pos >= 0 and self._table[pos] not in (self._VIDE, self._SUPPRIME):
            self._table[pos] = self._SUPPRIME
            self._taille -= 1
            return True
        return False

    def _redimensionner(self) -> None:
        ancienne_table = self._table
        self._capacite *= 2
        self._table = [self._VIDE] * self._capacite
        self._taille = 0
        for cellule in ancienne_table:
            if cellule not in (self._VIDE, self._SUPPRIME):
                tel, info = cellule
                self.inserer(tel, info['id'], info['role'], info['username'])

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"UtilisateurHashTable(taille={self._taille}, capacite={self._capacite})"





class DemandeDeblockageHeap:

    def __init__(self):
        self._heap: list[tuple] = []

    def ajouter(self, id_utilisateur: int, telephone: str,
                date_demande: datetime, motif: str = '') -> None:
        
        ts = date_demande.timestamp()
        heapq.heappush(self._heap, (ts, id_utilisateur, telephone, motif))

    def retirer_plus_prioritaire(self) -> dict | None:
        if self._heap:
            ts, uid, tel, motif = heapq.heappop(self._heap)
            return {'id_utilisateur': uid, 'telephone': tel,
                    'date_demande': datetime.fromtimestamp(ts), 'motif': motif}
        return None

    def apercu(self) -> dict | None:
        if self._heap:
            ts, uid, tel, motif = self._heap[0]
            return {'id_utilisateur': uid, 'telephone': tel,
                    'date_demande': datetime.fromtimestamp(ts), 'motif': motif}
        return None

    def taille(self) -> int:
        return len(self._heap)

    def __repr__(self):
        return f"DemandeDeblockageHeap(en_attente={len(self._heap)})"





class GrapheUtilisateurs:

    def __init__(self):
        
        self._adj: dict[int, dict[int, dict]] = {}

    def ajouter_noeud(self, id_utilisateur: int) -> None:
        if id_utilisateur not in self._adj:
            self._adj[id_utilisateur] = {}

    def ajouter_arete(self, source: int, cible: int,
                      type_relation: str = 'transaction', poids: float = 1.0) -> None:
        self.ajouter_noeud(source)
        self.ajouter_noeud(cible)
        if cible in self._adj[source]:
            self._adj[source][cible]['poids'] += poids
        else:
            self._adj[source][cible] = {'poids': poids, 'type': type_relation}

    def voisins(self, id_utilisateur: int) -> dict[int, dict]:
        return self._adj.get(id_utilisateur, {})

    def degre_sortant(self, id_utilisateur: int) -> int:
        return len(self._adj.get(id_utilisateur, {}))

    def poids_total(self, source: int, cible: int) -> float:
        return self._adj.get(source, {}).get(cible, {}).get('poids', 0.0)

    def supprimer_noeud(self, id_utilisateur: int) -> None:
        """Supprime un nœud et toutes ses arêtes entrantes/sortantes."""
        self._adj.pop(id_utilisateur, None)
        for voisins in self._adj.values():
            voisins.pop(id_utilisateur, None)

    def bfs(self, depart: int) -> list[int]:
        """Parcours en largeur depuis un nœud."""
        visites = []
        file = [depart]
        vus = {depart}
        while file:
            noeud = file.pop(0)
            visites.append(noeud)
            for voisin in self._adj.get(noeud, {}):
                if voisin not in vus:
                    vus.add(voisin)
                    file.append(voisin)
        return visites

    def nb_noeuds(self) -> int:
        return len(self._adj)

    def __repr__(self):
        nb_aretes = sum(len(v) for v in self._adj.values())
        return f"GrapheUtilisateurs(noeuds={len(self._adj)}, arêtes={nb_aretes})"





class NoeudAVL:
    __slots__ = ('cle', 'valeur', 'hauteur', 'gauche', 'droit')

    def __init__(self, cle: str, valeur):
        self.cle = cle
        self.valeur = valeur
        self.hauteur = 1
        self.gauche: 'NoeudAVL | None' = None
        self.droit: 'NoeudAVL | None' = None


class AVLUtilisateurs:

    def __init__(self):
        self._racine: NoeudAVL | None = None
        self._taille = 0

    

    @staticmethod
    def _hauteur(n: NoeudAVL | None) -> int:
        return n.hauteur if n else 0

    def _facteur(self, n: NoeudAVL) -> int:
        return self._hauteur(n.gauche) - self._hauteur(n.droit)

    def _update_hauteur(self, n: NoeudAVL) -> None:
        n.hauteur = 1 + max(self._hauteur(n.gauche), self._hauteur(n.droit))

    def _rotation_droite(self, z: NoeudAVL) -> NoeudAVL:
        y = z.gauche
        T3 = y.droit
        y.droit = z
        z.gauche = T3
        self._update_hauteur(z)
        self._update_hauteur(y)
        return y

    def _rotation_gauche(self, z: NoeudAVL) -> NoeudAVL:
        y = z.droit
        T2 = y.gauche
        y.gauche = z
        z.droit = T2
        self._update_hauteur(z)
        self._update_hauteur(y)
        return y

    def _equilibrer(self, n: NoeudAVL) -> NoeudAVL:
        self._update_hauteur(n)
        fb = self._facteur(n)
        if fb > 1:
            if self._facteur(n.gauche) < 0:
                n.gauche = self._rotation_gauche(n.gauche)
            return self._rotation_droite(n)
        if fb < -1:
            if self._facteur(n.droit) > 0:
                n.droit = self._rotation_droite(n.droit)
            return self._rotation_gauche(n)
        return n

    

    def _inserer(self, noeud: NoeudAVL | None, cle: str, valeur) -> NoeudAVL:
        if not noeud:
            self._taille += 1
            return NoeudAVL(cle, valeur)
        if cle < noeud.cle:
            noeud.gauche = self._inserer(noeud.gauche, cle, valeur)
        elif cle > noeud.cle:
            noeud.droit = self._inserer(noeud.droit, cle, valeur)
        else:
            noeud.valeur = valeur   
        return self._equilibrer(noeud)

    def inserer(self, username: str, id_utilisateur: int) -> None:
        self._racine = self._inserer(self._racine, username, id_utilisateur)

    def _chercher(self, noeud: NoeudAVL | None, cle: str):
        if not noeud:
            return None
        if cle == noeud.cle:
            return noeud.valeur
        if cle < noeud.cle:
            return self._chercher(noeud.gauche, cle)
        return self._chercher(noeud.droit, cle)

    def chercher(self, username: str) -> int | None:
        """Retourne l'id_utilisateur ou None."""
        return self._chercher(self._racine, username)

    def _inordre(self, noeud: NoeudAVL | None, resultat: list) -> None:
        if noeud:
            self._inordre(noeud.gauche, resultat)
            resultat.append((noeud.cle, noeud.valeur))
            self._inordre(noeud.droit, resultat)

    def liste_ordonnee(self) -> list[tuple[str, int]]:
        """Retourne tous les (username, id) triés alphabétiquement."""
        r: list = []
        self._inordre(self._racine, r)
        return r

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"AVLUtilisateurs(taille={self._taille}, hauteur={self._hauteur(self._racine)})"





index_telephone = UtilisateurHashTable()
file_deblocage = DemandeDeblockageHeap()
graphe_utilisateurs = GrapheUtilisateurs()
avl_usernames = AVLUtilisateurs()
