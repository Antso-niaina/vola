
import heapq
from decimal import Decimal





def resoudre_qr_greedy(codes_candidats: list[dict]) -> dict | None:
    actifs = [c for c in codes_candidats if c.get('actif', False)]
    if not actifs:
        return None
    
    return max(actifs, key=lambda c: c.get('date_creation') or 0)





def ordonner_paiements(paiements: list[dict]) -> list[dict]:
    heap = []
    for i, p in enumerate(paiements):
        montant = -float(p.get('montant', 0))  
        ts = p['date_paiement'].timestamp() if p.get('date_paiement') else i
        heapq.heappush(heap, (montant, ts, i, p))

    return [heapq.heappop(heap)[3] for _ in range(len(heap))]





class NoeudDecisionPaiement:
    def __init__(self, condition=None, vrai=None, faux=None,
                 resultat: str = None, motif: str = ''):
        self.condition = condition
        self.vrai = vrai
        self.faux = faux
        self.resultat = resultat
        self.motif = motif


def construire_arbre_validation_paiement() -> NoeudDecisionPaiement:
    return NoeudDecisionPaiement(
        condition=lambda c: c.get('qr_valide', False),
        faux=NoeudDecisionPaiement(resultat='QR_INVALIDE', motif='Code QR introuvable ou inactif'),
        vrai=NoeudDecisionPaiement(
            condition=lambda c: c.get('client_different_commercant', True),
            faux=NoeudDecisionPaiement(resultat='AUTO_PAIEMENT', motif='Impossible de se payer soi-même'),
            vrai=NoeudDecisionPaiement(
                condition=lambda c: c.get('client_actif', False),
                faux=NoeudDecisionPaiement(resultat='CLIENT_BLOQUE', motif='Compte client bloqué ou suspendu'),
                vrai=NoeudDecisionPaiement(
                    condition=lambda c: c.get('solde_suffisant', False),
                    faux=NoeudDecisionPaiement(resultat='INSUFFISANT', motif='Solde client insuffisant'),
                    vrai=NoeudDecisionPaiement(resultat='VALIDE', motif='Paiement QR autorisé'),
                )
            )
        )
    )


def _evaluer(noeud: NoeudDecisionPaiement, ctx: dict) -> tuple[str, str]:
    if noeud.resultat is not None:
        return noeud.resultat, noeud.motif
    if noeud.condition and noeud.condition(ctx):
        return _evaluer(noeud.vrai, ctx)
    return _evaluer(noeud.faux, ctx)


def valider_paiement_qr(
    qr_valide: bool,
    client_different_commercant: bool,
    client_actif: bool,
    solde_suffisant: bool,
) -> tuple[str, str]:
    arbre = construire_arbre_validation_paiement()
    ctx = {
        'qr_valide': qr_valide,
        'client_different_commercant': client_different_commercant,
        'client_actif': client_actif,
        'solde_suffisant': solde_suffisant,
    }
    return _evaluer(arbre, ctx)





def top_k_commercants_ca(commercants_stats: list[dict], k: int = 10) -> list[dict]:
    tas: list[tuple] = []

    for c in commercants_stats:
        ca = float(c.get('total_recu', 0))
        cid = c.get('id_commercant', 0)
        heapq.heappush(tas, (ca, cid, c))
        if len(tas) > k:
            heapq.heappop(tas)

    return [item[2] for item in sorted(tas, key=lambda x: -x[0])]
