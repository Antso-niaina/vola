"""
- Hash Table  : cache des OTP actifs (telephone → code/expiration)
- Tas binaire : file de priorité des tentatives de connexion (rate-limiting)
- Graphe      : réseau de sessions actives par utilisateur
"""

import heapq
from datetime import datetime


class OTPHashTable:

    def __init__(self, taille: int = 128):
        self._taille = taille
        self._buckets: list[list] = [[] for _ in range(taille)]
        self._nb_elements = 0


    def _hash(self, cle: str) -> int:
        h = 0
        for c in cle:
            h = (h * 31 + ord(c)) % self._taille
        return h

    def _trouver_dans_bucket(self, bucket: list, cle: str):
        for i, (k, v) in enumerate(bucket):
            if k == cle:
                return i, v
        return -1, None


    def inserer(self, telephone: str, code: str, expiration: datetime) -> None:
        idx = self._hash(telephone)
        bucket = self._buckets[idx]
        pos, _ = self._trouver_dans_bucket(bucket, telephone)
        entree = {'code': code, 'expiration': expiration, 'utilise': False}
        if pos >= 0:
            bucket[pos] = (telephone, entree)
        else:
            bucket.append((telephone, entree))
            self._nb_elements += 1

    def obtenir(self, telephone: str) -> dict | None:
        idx = self._hash(telephone)
        _, valeur = self._trouver_dans_bucket(self._buckets[idx], telephone)
        return valeur

    def marquer_utilise(self, telephone: str) -> bool:
        idx = self._hash(telephone)
        pos, valeur = self._trouver_dans_bucket(self._buckets[idx], telephone)
        if pos >= 0 and valeur:
            valeur['utilise'] = True
            return True
        return False

    def supprimer(self, telephone: str) -> bool:
        idx = self._hash(telephone)
        bucket = self._buckets[idx]
        pos, _ = self._trouver_dans_bucket(bucket, telephone)
        if pos >= 0:
            bucket.pop(pos)
            self._nb_elements -= 1
            return True
        return False

    def est_valide(self, telephone: str, code: str) -> bool:
        entree = self.obtenir(telephone)
        if not entree:
            return False
        if entree['utilise']:
            return False
        if entree['code'] != code:
            return False
        if datetime.now().astimezone() > entree['expiration'].astimezone():
            return False
        return True

    def purger_expires(self) -> int:
        maintenant = datetime.now().astimezone()
        supprimes = 0
        for bucket in self._buckets:
            a_supprimer = [
                k for k, v in bucket
                if v['utilise'] or v['expiration'].astimezone() < maintenant
            ]
            for k in a_supprimer:
                self.supprimer(k)
                supprimes += 1
        return supprimes

    def taille(self) -> int:
        return self._nb_elements

    def __repr__(self):
        return f"OTPHashTable(éléments={self._nb_elements}, buckets={self._taille})"


class TentativeHeap:
    def __init__(self):
        self._heap: list[tuple] = []

    def ajouter(self, timestamp: float, telephone: str,
                ip: str, type_tentative: str, succes: bool) -> None:
        heapq.heappush(self._heap, (timestamp, telephone, ip, type_tentative, succes))

    def retirer_plus_ancienne(self) -> tuple | None:
        if self._heap:
            return heapq.heappop(self._heap)
        return None

    def peek_plus_ancienne(self) -> tuple | None:
        """Consulte sans retirer."""
        return self._heap[0] if self._heap else None

    def compter_echecs_recents(self, telephone: str,
                               depuis_timestamp: float,
                               type_tentative: str = 'otp') -> int:
        return sum(
            1 for ts, tel, _, typ, succes in self._heap
            if tel == telephone
            and typ == type_tentative
            and not succes
            and ts >= depuis_timestamp
        )

    def purger_avant(self, timestamp_limite: float) -> int:
        avant = len(self._heap)
        self._heap = [
            t for t in self._heap if t[0] >= timestamp_limite
        ]
        heapq.heapify(self._heap)
        return avant - len(self._heap)

    def taille(self) -> int:
        return len(self._heap)

    def __repr__(self):
        return f"TentativeHeap(éléments={len(self._heap)})"


class GrapheSessionsAuth:

    def __init__(self):
        self._adjacence: dict[int, list[dict]] = {}

    def ajouter_utilisateur(self, id_utilisateur: int) -> None:
        if id_utilisateur not in self._adjacence:
            self._adjacence[id_utilisateur] = []

    def ajouter_session(self, id_utilisateur: int,
                        jti: str, ip: str, date_creation: datetime) -> None:
        self.ajouter_utilisateur(id_utilisateur)
        self._adjacence[id_utilisateur].append({
            'jti': jti,
            'ip': ip,
            'date_creation': date_creation,
        })

    def sessions_de(self, id_utilisateur: int) -> list[dict]:
        return self._adjacence.get(id_utilisateur, [])

    def revoquer_session(self, id_utilisateur: int, jti: str) -> bool:
        sessions = self._adjacence.get(id_utilisateur, [])
        avant = len(sessions)
        self._adjacence[id_utilisateur] = [s for s in sessions if s['jti'] != jti]
        return len(self._adjacence[id_utilisateur]) < avant

    def revoquer_toutes(self, id_utilisateur: int) -> int:
        """Révoque toutes les sessions. Retourne le nombre révoqué."""
        nb = len(self._adjacence.get(id_utilisateur, []))
        self._adjacence[id_utilisateur] = []
        return nb

    def nb_sessions_actives(self, id_utilisateur: int) -> int:
        return len(self._adjacence.get(id_utilisateur, []))

    def utilisateurs_actifs(self) -> list[int]:
        return [uid for uid, sessions in self._adjacence.items() if sessions]

    def __repr__(self):
        total = sum(len(v) for v in self._adjacence.values())
        return f"GrapheSessionsAuth(utilisateurs={len(self._adjacence)}, sessions={total})"


otp_cache = OTPHashTable()
tentative_heap = TentativeHeap()
graphe_sessions = GrapheSessionsAuth()
