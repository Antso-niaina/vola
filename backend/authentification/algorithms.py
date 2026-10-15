
import heapq
from datetime import datetime, timedelta, timezone
from typing import Optional





def selectionner_meilleur_otp(otps: list[dict]) -> Optional[dict]:
    maintenant = datetime.now(tz=timezone.utc)
    meilleur = None
    meilleur_delai = timedelta(0)

    for otp in otps:
        if otp.get('utilise', True):
            continue
        expiration = otp['expiration']
        
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        delai = expiration - maintenant
        if delai > timedelta(0) and delai > meilleur_delai:
            meilleur = otp
            meilleur_delai = delai

    return meilleur





def ordonner_tentatives_suspectes(tentatives: list[dict], top_n: int = 10) -> list[dict]:
    agregats: dict[str, dict] = {}
    for t in tentatives:
        tel = t.get('telephone', '')
        if tel not in agregats:
            agregats[tel] = {'telephone': tel, 'nb_echecs': 0, 'ips': set(), 'tentatives': []}
        if not t.get('succes', True):
            agregats[tel]['nb_echecs'] += 1
        agregats[tel]['ips'].add(t.get('ip', ''))
        agregats[tel]['tentatives'].append(t)

    
    scored = []
    for tel, info in agregats.items():
        nb_ips_distinctes = len(info['ips'])
        score = info['nb_echecs'] * 3 + (2 if nb_ips_distinctes > 2 else 0)
        scored.append({
            'telephone': tel,
            'score_suspicion': score,
            'nb_echecs': info['nb_echecs'],
            'nb_ips_distinctes': nb_ips_distinctes,
            'ips': list(info['ips']),
        })

    
    return heapq.nlargest(top_n, scored, key=lambda x: x['score_suspicion'])





class NoeudDecision:

    def __init__(self, condition=None, vrai=None, faux=None, resultat=None, motif: str = ''):
        self.condition = condition   
        self.vrai = vrai             
        self.faux = faux             
        self.resultat = resultat     
        self.motif = motif           


def construire_arbre_validation_connexion() -> NoeudDecision:

    feuille_bloque = NoeudDecision(resultat='BLOQUE', motif='Compte suspendu ou bloqué')
    feuille_rate = NoeudDecision(resultat='RATE_LIMITED', motif='Trop de tentatives échouées')
    feuille_echec = NoeudDecision(resultat='ECHEC_OTP', motif='Code OTP invalide ou expiré')
    feuille_succes = NoeudDecision(resultat='SUCCES', motif='Connexion autorisée')

    noeud_otp = NoeudDecision(
        condition=lambda ctx: ctx.get('otp_valide', False),
        vrai=feuille_succes,
        faux=feuille_echec,
    )

    noeud_rate = NoeudDecision(
        condition=lambda ctx: ctx.get('nb_echecs_recents', 0) >= 5,
        vrai=feuille_rate,
        faux=noeud_otp,
    )

    racine = NoeudDecision(
        condition=lambda ctx: ctx.get('compte_actif', False),
        vrai=noeud_rate,
        faux=feuille_bloque,
    )

    return racine


def evaluer_arbre(noeud: NoeudDecision, contexte: dict) -> tuple[str, str]:
    if noeud.resultat is not None:
        return noeud.resultat, noeud.motif

    if noeud.condition and noeud.condition(contexte):
        return evaluer_arbre(noeud.vrai, contexte)
    else:
        return evaluer_arbre(noeud.faux, contexte)


def valider_connexion(compte_actif: bool,
                      nb_echecs_recents: int,
                      otp_valide: bool) -> tuple[str, str]:
    arbre = construire_arbre_validation_connexion()
    contexte = {
        'compte_actif': compte_actif,
        'nb_echecs_recents': nb_echecs_recents,
        'otp_valide': otp_valide,
    }
    return evaluer_arbre(arbre, contexte)





def top_k_ips_suspectes(tentatives: list[dict], k: int = 5) -> list[dict]:
    compteur: dict[str, dict] = {}
    for t in tentatives:
        ip = t.get('ip_address') or t.get('ip', 'inconnue')
        if not t.get('succes', True):
            if ip not in compteur:
                compteur[ip] = {'ip': ip, 'nb_echecs': 0, 'telephones': set()}
            compteur[ip]['nb_echecs'] += 1
            compteur[ip]['telephones'].add(t.get('telephone', ''))

    
    tas = []
    for ip, info in compteur.items():
        heapq.heappush(tas, (info['nb_echecs'], ip))
        if len(tas) > k:
            heapq.heappop(tas)

    
    resultat = []
    while tas:
        nb, ip = heapq.heappop(tas)
        info = compteur[ip]
        resultat.append({
            'ip': ip,
            'nb_echecs': nb,
            'telephones': list(info['telephones']),
        })

    resultat.reverse()
    return resultat
