

import heapq
from decimal import Decimal
from typing import Optional





def optimiser_transferts_greedy(
    solde_disponible: Decimal,
    demandes: list[dict]
) -> list[dict]:
    
    triees = sorted(demandes,
                    key=lambda d: (-d.get('priorite', 0), d.get('montant', Decimal(0))))

    selectionnees = []
    solde_restant = solde_disponible

    for demande in triees:
        montant = demande.get('montant', Decimal(0))
        if montant <= solde_restant:
            selectionnees.append(demande)
            solde_restant -= montant

    return selectionnees





def ordonner_transferts(transferts: list[dict]) -> list[dict]:
    heap = []
    for i, t in enumerate(transferts):
        priorite = -t.get('priorite', 0)             
        montant = -float(t.get('montant', 0))         
        ts = t.get('date_creation').timestamp() if t.get('date_creation') else i
        heapq.heappush(heap, (priorite, montant, ts, i, t))

    return [item[4] for item in [heapq.heappop(heap) for _ in range(len(heap))]]





class NoeudDecisionTransfert:
    def __init__(self, condition=None, vrai=None, faux=None,
                 resultat: str = None, motif: str = ''):
        self.condition = condition
        self.vrai = vrai
        self.faux = faux
        self.resultat = resultat
        self.motif = motif


def construire_arbre_validation_transfert() -> NoeudDecisionTransfert:
    return NoeudDecisionTransfert(
        condition=lambda c: c.get('expediteur_actif', False),
        faux=NoeudDecisionTransfert(resultat='BLOQUE', motif='Compte expéditeur bloqué ou suspendu'),
        vrai=NoeudDecisionTransfert(
            condition=lambda c: c.get('destinataire_actif', False),
            faux=NoeudDecisionTransfert(resultat='BLOQUE', motif='Compte destinataire bloqué ou suspendu'),
            vrai=NoeudDecisionTransfert(
                condition=lambda c: c.get('solde_suffisant', False),
                faux=NoeudDecisionTransfert(resultat='INSUFFISANT', motif='Solde insuffisant'),
                vrai=NoeudDecisionTransfert(
                    condition=lambda c: c.get('dans_limite_journaliere', True),
                    faux=NoeudDecisionTransfert(resultat='LIMITE', motif='Limite journalière dépassée'),
                    vrai=NoeudDecisionTransfert(resultat='VALIDE', motif='Transfert autorisé'),
                )
            )
        )
    )


def evaluer_validation_transfert(noeud: NoeudDecisionTransfert, ctx: dict) -> tuple[str, str]:
    if noeud.resultat is not None:
        return noeud.resultat, noeud.motif
    if noeud.condition and noeud.condition(ctx):
        return evaluer_validation_transfert(noeud.vrai, ctx)
    return evaluer_validation_transfert(noeud.faux, ctx)


def valider_transfert(
    expediteur_actif: bool,
    destinataire_actif: bool,
    solde_suffisant: bool,
    dans_limite_journaliere: bool = True,
) -> tuple[str, str]:
    arbre = construire_arbre_validation_transfert()
    contexte = {
        'expediteur_actif': expediteur_actif,
        'destinataire_actif': destinataire_actif,
        'solde_suffisant': solde_suffisant,
        'dans_limite_journaliere': dans_limite_journaliere,
    }
    return evaluer_validation_transfert(arbre, contexte)





def top_k_portefeuilles_actifs(portefeuilles_stats: list[dict], k: int = 10) -> list[dict]:
    tas: list[tuple] = []

    for p in portefeuilles_stats:
        volume = float(p.get('volume_total', 0))
        pid = p.get('id_portefeuille', 0)
        heapq.heappush(tas, (volume, pid, p))
        if len(tas) > k:
            heapq.heappop(tas)

    return [item[2] for item in sorted(tas, key=lambda x: -x[0])]
