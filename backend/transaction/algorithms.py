

import heapq
from decimal import Decimal
from datetime import datetime





def selectionner_demandes_greedy(
    demandes: list[dict],
    capacite_admin: int = 50,
) -> list[dict]:
    
    triees = sorted(demandes, key=lambda d: float(d.get('montant', 0)), reverse=True)
    return triees[:capacite_admin]





def ordonner_validations(validations: list[dict]) -> list[dict]:
    POIDS_TYPE = {'retrait': 2, 'depot': 1}

    heap = []
    for i, v in enumerate(validations):
        poids = -POIDS_TYPE.get(v.get('type', 'depot'), 1)
        montant = -float(v.get('montant', 0))
        ts = v['date_demande'].timestamp() if v.get('date_demande') else i
        heapq.heappush(heap, (poids, montant, ts, i, v))

    return [heapq.heappop(heap)[4] for _ in range(len(heap))]


class NoeudDecisionValidation:
    def __init__(self, condition=None, vrai=None, faux=None,
                 resultat: str = None, motif: str = ''):
        self.condition = condition
        self.vrai = vrai
        self.faux = faux
        self.resultat = resultat
        self.motif = motif


def construire_arbre_validation_depot() -> NoeudDecisionValidation:
    return NoeudDecisionValidation(
        condition=lambda c: c.get('admin_peut_valider', False),
        faux=NoeudDecisionValidation(resultat='REFUSE', motif="Admin sans permission de valider les dépôts"),
        vrai=NoeudDecisionValidation(
            condition=lambda c: c.get('depot_en_attente', False),
            faux=NoeudDecisionValidation(resultat='DEJA_TRAITE', motif="Dépôt déjà traité ou introuvable"),
            vrai=NoeudDecisionValidation(
                condition=lambda c: c.get('montant_valide', False),
                faux=NoeudDecisionValidation(resultat='INVALIDE', motif="Montant hors des limites autorisées"),
                vrai=NoeudDecisionValidation(resultat='VALIDE', motif="Dépôt validé avec succès"),
            )
        )
    )


def construire_arbre_validation_retrait() -> NoeudDecisionValidation:
    return NoeudDecisionValidation(
        condition=lambda c: c.get('admin_peut_valider', False),
        faux=NoeudDecisionValidation(resultat='REFUSE', motif="Admin sans permission de valider les retraits"),
        vrai=NoeudDecisionValidation(
            condition=lambda c: c.get('retrait_en_attente', False),
            faux=NoeudDecisionValidation(resultat='DEJA_TRAITE', motif="Retrait déjà traité ou introuvable"),
            vrai=NoeudDecisionValidation(
                condition=lambda c: c.get('solde_suffisant', False),
                faux=NoeudDecisionValidation(resultat='SOLDE_INSUFFISANT', motif="Solde insuffisant pour ce retrait"),
                vrai=NoeudDecisionValidation(resultat='VALIDE', motif="Retrait validé avec succès"),
            )
        )
    )


def _evaluer(noeud: NoeudDecisionValidation, ctx: dict) -> tuple[str, str]:
    if noeud.resultat is not None:
        return noeud.resultat, noeud.motif
    if noeud.condition and noeud.condition(ctx):
        return _evaluer(noeud.vrai, ctx)
    return _evaluer(noeud.faux, ctx)


def valider_depot(admin_peut_valider: bool,depot_en_attente: bool,montant_valide: bool) -> tuple[str, str]:
    return _evaluer(
        construire_arbre_validation_depot(),
        {'admin_peut_valider': admin_peut_valider,
         'depot_en_attente': depot_en_attente,
         'montant_valide': montant_valide}
    )


def valider_retrait(admin_peut_valider: bool,retrait_en_attente: bool,solde_suffisant: bool) -> tuple[str, str]:
    return _evaluer(
        construire_arbre_validation_retrait(),
        {'admin_peut_valider': admin_peut_valider,
         'retrait_en_attente': retrait_en_attente,
         'solde_suffisant': solde_suffisant}
    )


def top_k_transactions_montant(transactions: list[dict], k: int = 10) -> list[dict]:
    tas: list[tuple] = []
    for t in transactions:
        montant = float(t.get('montant', 0))
        tid = t.get('id_transaction', 0)
        heapq.heappush(tas, (montant, tid, t))
        if len(tas) > k:
            heapq.heappop(tas)

    return [item[2] for item in sorted(tas, key=lambda x: -x[0])]
