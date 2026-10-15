

import heapq
from decimal import Decimal
from datetime import datetime, timedelta





METRIQUES_DISPONIBLES = [
    {'nom': 'total_utilisateurs',     'interet': 5, 'cout_calcul': 1},
    {'nom': 'total_transactions',     'interet': 8, 'cout_calcul': 2},
    {'nom': 'volume_total',           'interet': 9, 'cout_calcul': 2},
    {'nom': 'top_commercants',        'interet': 7, 'cout_calcul': 4},
    {'nom': 'top_utilisateurs',       'interet': 6, 'cout_calcul': 3},
    {'nom': 'transactions_par_jour',  'interet': 8, 'cout_calcul': 5},
    {'nom': 'depots_en_attente',      'interet': 9, 'cout_calcul': 1},
    {'nom': 'retraits_en_attente',    'interet': 9, 'cout_calcul': 1},
]


def selectionner_metriques_greedy(quota_calcul: int = 15,metriques: list[dict] = None) -> list[str]:

    if metriques is None:
        metriques = METRIQUES_DISPONIBLES

    triees = sorted(metriques, key=lambda m: m['interet'] / m['cout_calcul'], reverse=True)

    selectionnees = []
    budget_restant = quota_calcul

    for m in triees:
        if m['cout_calcul'] <= budget_restant:
            selectionnees.append(m['nom'])
            budget_restant -= m['cout_calcul']

    return selectionnees





def ordonner_alertes_admin(alertes: list[dict]) -> list[dict]:
    URGENCE = {
        'alerte_fraude': 10,
        'retrait_en_attente_urgent': 10,
        'depot_en_attente_urgent': 9,
        'retrait_en_attente': 6,
        'depot_en_attente': 5,
        'rapport_quotidien': 1,
    }

    maintenant = datetime.now()
    heap = []

    for i, alerte in enumerate(alertes):
        type_alerte = alerte.get('type', '')
        date_creation = alerte.get('date_creation')

        
        if date_creation and (maintenant - date_creation) > timedelta(hours=24):
            if type_alerte == 'retrait_en_attente':
                type_alerte = 'retrait_en_attente_urgent'
            elif type_alerte == 'depot_en_attente':
                type_alerte = 'depot_en_attente_urgent'

        urgence = -URGENCE.get(type_alerte, 1)
        montant = -float(alerte.get('montant', 0))
        ts = date_creation.timestamp() if date_creation else i

        heapq.heappush(heap, (urgence, montant, ts, i, alerte))

    return [heapq.heappop(heap)[4] for _ in range(len(heap))]





class NoeudDecisionSuspicion:
    def __init__(self, condition=None, vrai=None, faux=None,
                 resultat: str = None, motif: str = ''):
        self.condition = condition
        self.vrai = vrai
        self.faux = faux
        self.resultat = resultat
        self.motif = motif


def construire_arbre_suspicion() -> NoeudDecisionSuspicion:
    return NoeudDecisionSuspicion(
        condition=lambda c: float(c.get('montant', 0)) > c.get('seuil_haut', 1_000_000),
        vrai=NoeudDecisionSuspicion(resultat='TRES_SUSPECTE', motif='Montant anormalement élevé'),
        faux=NoeudDecisionSuspicion(
            condition=lambda c: c.get('nb_transactions_recentes', 0) > c.get('seuil_freq', 20),
            vrai=NoeudDecisionSuspicion(resultat='SUSPECTE', motif='Fréquence anormalement haute'),
            faux=NoeudDecisionSuspicion(
                condition=lambda c: c.get('pattern_inhabituel', False),
                vrai=NoeudDecisionSuspicion(resultat='A_SURVEILLER', motif='Comportement inhabituel détecté'),
                faux=NoeudDecisionSuspicion(resultat='NORMALE', motif='Transaction dans les normes'),
            )
        )
    )


def _evaluer(noeud: NoeudDecisionSuspicion, ctx: dict) -> tuple[str, str]:
    if noeud.resultat is not None:
        return noeud.resultat, noeud.motif
    if noeud.condition and noeud.condition(ctx):
        return _evaluer(noeud.vrai, ctx)
    return _evaluer(noeud.faux, ctx)


def classifier_transaction(
    montant: float,
    nb_transactions_recentes: int,
    pattern_inhabituel: bool = False,
    seuil_haut: float = 1_000_000,
    seuil_freq: int = 20,
) -> tuple[str, str]:
    arbre = construire_arbre_suspicion()
    ctx = {
        'montant': montant,
        'nb_transactions_recentes': nb_transactions_recentes,
        'pattern_inhabituel': pattern_inhabituel,
        'seuil_haut': seuil_haut,
        'seuil_freq': seuil_freq,
    }
    return _evaluer(arbre, ctx)


def analyser_transactions_batch(transactions: list[dict],
                                 seuil_haut: float = 1_000_000,
                                 seuil_freq: int = 20) -> list[dict]:
    
    compteur: dict[int, int] = {}
    for t in transactions:
        exp = t.get('id_expediteur', 0)
        compteur[exp] = compteur.get(exp, 0) + 1

    suspectes = []
    for t in transactions:
        montant = float(t.get('montant', 0))
        exp = t.get('id_expediteur', 0)
        nb_recentes = compteur.get(exp, 0)

        niveau, motif = classifier_transaction(
            montant=montant,
            nb_transactions_recentes=nb_recentes,
            seuil_haut=seuil_haut,
            seuil_freq=seuil_freq,
        )

        if niveau != 'NORMALE':
            suspectes.append({**t, 'niveau_suspicion': niveau, 'motif': motif})

    return suspectes





def top_k_multi_criteres(entites: list[dict], k: int = 10,
                          critere: str = 'volume') -> list[dict]:
    champ = 'volume_total' if critere == 'volume' else 'nb_transactions'

    tas: list[tuple] = []
    for i, e in enumerate(entites):
        score = float(e.get(champ, 0))
        heapq.heappush(tas, (score, i, e))
        if len(tas) > k:
            heapq.heappop(tas)

    return [item[2] for item in sorted(tas, key=lambda x: -x[0])]
