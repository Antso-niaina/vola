

import heapq
from decimal import Decimal
from datetime import datetime, date





class StatsHashTable:

    def __init__(self, capacite: int = 64):
        self._capacite = capacite
        self._buckets: list[list] = [[] for _ in range(capacite)]
        self._taille = 0

    def _hash(self, cle: str) -> int:
        h = 0
        for c in cle:
            h = (h * 31 + ord(c)) % self._capacite
        return h

    def inserer(self, type_stat: str, periode: str, donnees: dict) -> None:
        cle = f"{type_stat}_{periode}"
        idx = self._hash(cle)
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == cle:
                self._buckets[idx][i] = (cle, {**donnees, 'calcule_le': datetime.now()})
                return
        self._buckets[idx].append((cle, {**donnees, 'calcule_le': datetime.now()}))
        self._taille += 1

    def obtenir(self, type_stat: str, periode: str) -> dict | None:
        cle = f"{type_stat}_{periode}"
        idx = self._hash(cle)
        for k, v in self._buckets[idx]:
            if k == cle:
                return v
        return None

    def invalider(self, type_stat: str, periode: str) -> bool:
        cle = f"{type_stat}_{periode}"
        idx = self._hash(cle)
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == cle:
                self._buckets[idx].pop(i)
                self._taille -= 1
                return True
        return False

    def taille(self) -> int:
        return self._taille

    def __repr__(self):
        return f"StatsHashTable(entrees={self._taille})"





class TopNHeap:

    def __init__(self, n: int = 10):
        self._n = n
        self._heap: list[tuple] = []
        self._index: dict[int, float] = {}  

    def ajouter_ou_mettre_a_jour(self, identifiant: int,
                                  score: float, meta: dict) -> None:
        if identifiant in self._index:
            
            self._index[identifiant] = score
        else:
            self._index[identifiant] = score

        heapq.heappush(self._heap, (score, identifiant, meta))

        
        while len(self._heap) > self._n * 3:  
            heapq.heappop(self._heap)

    def top(self) -> list[dict]:
        """Retourne le top-N trié par score décroissant."""
        vus: set[int] = set()
        resultat = []
        temp = sorted(self._heap, key=lambda x: -x[0])

        for score, uid, meta in temp:
            if uid in vus:
                continue
            vus.add(uid)
            score_reel = self._index.get(uid, score)
            resultat.append({**meta, 'score': score_reel})
            if len(resultat) >= self._n:
                break

        return resultat

    def score_minimum(self) -> float:
        return self._heap[0][0] if self._heap else 0.0

    def __repr__(self):
        return f"TopNHeap(N={self._n}, éléments={len(self._index)})"





class GrapheStatsGlobal:

    def __init__(self):
        self._adj: dict[str, dict[str, dict]] = {}

    def ajouter_noeud(self, noeud: str) -> None:
        if noeud not in self._adj:
            self._adj[noeud] = {}

    def enregistrer_flux(self, source: str, cible: str,
                         montant: float, nb: int = 1) -> None:
        self.ajouter_noeud(source)
        self.ajouter_noeud(cible)
        if cible not in self._adj[source]:
            self._adj[source][cible] = {'montant': 0.0, 'nb': 0}
        self._adj[source][cible]['montant'] += montant
        self._adj[source][cible]['nb'] += nb

    def flux_total(self, source: str) -> float:
        return sum(v['montant'] for v in self._adj.get(source, {}).values())

    def to_dict(self) -> dict:
        """Sérialise le graphe pour l'API."""
        noeuds = list(self._adj.keys())
        aretes = []
        for src, voisins in self._adj.items():
            for dest, info in voisins.items():
                aretes.append({
                    'source': src, 'cible': dest,
                    'montant': info['montant'], 'nb': info['nb']
                })
        return {'noeuds': noeuds, 'aretes': aretes}

    def __repr__(self):
        nb_aretes = sum(len(v) for v in self._adj.values())
        return f"GrapheStatsGlobal(noeuds={len(self._adj)}, flux={nb_aretes})"





class NoeudAVLPeriode:
    __slots__ = ('timestamp', 'donnees', 'hauteur', 'gauche', 'droit')

    def __init__(self, timestamp: float, donnees: dict):
        self.timestamp = timestamp
        self.donnees = donnees
        self.hauteur = 1
        self.gauche = None
        self.droit = None


class AVLStatsPeriode:

    def __init__(self):
        self._racine = None

    @staticmethod
    def _h(n) -> int:
        return n.hauteur if n else 0

    def _fb(self, n):
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

    def _ins(self, noeud, ts: float, donnees: dict):
        if not noeud:
            return NoeudAVLPeriode(ts, donnees)
        if ts < noeud.timestamp:
            noeud.gauche = self._ins(noeud.gauche, ts, donnees)
        elif ts > noeud.timestamp:
            noeud.droit = self._ins(noeud.droit, ts, donnees)
        else:
            
            noeud.donnees['nb'] = noeud.donnees.get('nb', 0) + donnees.get('nb', 0)
            noeud.donnees['volume'] = noeud.donnees.get('volume', 0) + donnees.get('volume', 0)
            return noeud
        return self._eq(noeud)

    def inserer(self, periode: date, nb_transactions: int, volume_total: float) -> None:
        import calendar
        ts = float(calendar.timegm(periode.timetuple()))
        self._racine = self._ins(self._racine, ts,
                                 {'nb': nb_transactions, 'volume': volume_total, 'date': str(periode)})

    def _range(self, noeud, ts_min: float, ts_max: float, res: list):
        if not noeud:
            return
        if noeud.timestamp > ts_min:
            self._range(noeud.gauche, ts_min, ts_max, res)
        if ts_min <= noeud.timestamp <= ts_max:
            res.append(noeud.donnees)
        if noeud.timestamp < ts_max:
            self._range(noeud.droit, ts_min, ts_max, res)

    def stats_entre(self, debut: date, fin: date) -> list[dict]:
        """Retourne les stats dans la plage [debut, fin]."""
        import calendar
        ts_min = float(calendar.timegm(debut.timetuple()))
        ts_max = float(calendar.timegm(fin.timetuple()))
        res: list[dict] = []
        self._range(self._racine, ts_min, ts_max, res)
        return sorted(res, key=lambda d: d.get('date', ''))

    def __repr__(self):
        return f"AVLStatsPeriode(hauteur={self._h(self._racine)})"





cache_stats = StatsHashTable()
top_utilisateurs_heap = TopNHeap(n=10)
top_commercants_heap = TopNHeap(n=10)
graphe_global = GrapheStatsGlobal()
avl_periodes = AVLStatsPeriode()
