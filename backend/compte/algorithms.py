

import heapq
from typing import Any





PERMISSIONS_DISPONIBLES = [
    {'nom': 'peut_valider_depot',     'priorite': 3, 'charge': 2},
    {'nom': 'peut_valider_retrait',   'priorite': 3, 'charge': 2},
    {'nom': 'peut_bloquer_utilisateur', 'priorite': 5, 'charge': 3},
]


def attribuer_permissions_greedy(charge_max: int,
                                 permissions: list[dict] = None) -> list[str]:
    if permissions is None:
        permissions = PERMISSIONS_DISPONIBLES

    
    triees = sorted(permissions, key=lambda p: p['priorite'] / p['charge'], reverse=True)

    attribuees = []
    charge_restante = charge_max

    for perm in triees:
        if perm['charge'] <= charge_restante:
            attribuees.append(perm['nom'])
            charge_restante -= perm['charge']

    return attribuees





def ordonner_demandes_modification(demandes: list[dict]) -> list[dict]:
    PRIORITE = {
        'deblocage': 10,
        'changement_role': 7,
        'mise_a_jour_profil': 3,
    }

    heap = []
    for i, d in enumerate(demandes):
        priorite = PRIORITE.get(d.get('type', ''), 1)
        
        ts = d.get('date').timestamp() if d.get('date') else i
        heapq.heappush(heap, (-priorite, ts, i, d))

    ordonnees = []
    while heap:
        _, _, _, demande = heapq.heappop(heap)
        ordonnees.append(demande)

    return ordonnees





class NoeudDecisionRole:
    def __init__(self, condition=None, vrai=None, faux=None, resultat=None):
        self.condition = condition
        self.vrai = vrai
        self.faux = faux
        self.resultat = resultat


def construire_arbre_role() -> NoeudDecisionRole:
    return NoeudDecisionRole(
        condition=lambda u: u.get('role') == 'client',
        vrai=NoeudDecisionRole(resultat='ClientSerializer'),
        faux=NoeudDecisionRole(
            condition=lambda u: u.get('role') == 'commercant',
            vrai=NoeudDecisionRole(resultat='CommercantSerializer'),
            faux=NoeudDecisionRole(
                condition=lambda u: u.get('role') == 'admin',
                vrai=NoeudDecisionRole(resultat='AdminSerializer'),
                faux=NoeudDecisionRole(resultat='UtilisateurSerializer'),
            )
        )
    )


def choisir_serialiseur(role: str) -> str:
    arbre = construire_arbre_role()
    noeud = arbre
    contexte = {'role': role}

    while noeud.resultat is None:
        if noeud.condition and noeud.condition(contexte):
            noeud = noeud.vrai
        else:
            noeud = noeud.faux

    return noeud.resultat





def top_k_utilisateurs_actifs(utilisateurs_stats: list[dict], k: int = 10) -> list[dict]:
    tas: list[tuple] = []

    for u in utilisateurs_stats:
        score = u.get('nb_transactions', 0)
        uid = u.get('id_utilisateur', 0)
        heapq.heappush(tas, (score, uid, u))
        if len(tas) > k:
            heapq.heappop(tas)

    
    resultat = [item[2] for item in sorted(tas, key=lambda x: -x[0])]
    return resultat
