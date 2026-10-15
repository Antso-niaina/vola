from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.db.models import Sum, Count, F

from compte.models import Utilisateurs
from commercants.models import PaiementsCommercants
from transaction.models import Transactions, Depots, Retrait
from statsAdmin.serializers import (
    NbrUtilisateursSerializer,
    NbrtransactionsSerializer,
    ListeDepotsAttenteSerializer,
    ListeRetraitsAttenteSerializer,
    TopCommercantsSerializer,
    TopUtilisateursSerializer,
    TransactionsParPeriodeSerializer,
)


from statsAdmin.data_structures import (
    cache_stats, top_utilisateurs_heap, top_commercants_heap,
    graphe_global, avl_periodes
)
from statsAdmin.algorithms import (
    selectionner_metriques_greedy,
    ordonner_alertes_admin,
    classifier_transaction,
    analyser_transactions_batch,
    top_k_multi_criteres,
)


class NbrUtilisateursView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        
        cached = cache_stats.obtenir('utilisateurs', 'global')
        if cached:
            serializer = NbrUtilisateursSerializer(cached)
            return Response({**serializer.data, '_cache': True}, status=status.HTTP_200_OK)

        total_utilisateurs = Utilisateurs.objects.count()
        total_clients = Utilisateurs.objects.filter(role='client').count()
        total_commercants = Utilisateurs.objects.filter(role='commercant').count()
        total_admins = Utilisateurs.objects.filter(role='admin').count()

        donnees = {
            'total_utilisateurs': total_utilisateurs,
            'total_clients': total_clients,
            'total_commercants': total_commercants,
            'total_admins': total_admins,
        }

        
        cache_stats.inserer('utilisateurs', 'global', donnees)

        serializer = NbrUtilisateursSerializer(donnees)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NbrTransactionsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        
        cached = cache_stats.obtenir('transactions', 'global')
        if cached:
            return Response({**cached, '_cache': True}, status=status.HTTP_200_OK)

        total_paiements = PaiementsCommercants.objects.count()
        total_depots = Depots.objects.count()
        total_retraits = Retrait.objects.count()
        total_transferts = Transactions.objects.filter(type_transaction='transfert').count()
        total_transactions = total_paiements + total_depots + total_retraits + total_transferts
        volume_total = Transactions.objects.aggregate(total=Sum('montant'))['total'] or 0

        donnees = {
            'total_transactions': total_transactions,
            'volume_total': volume_total,
            'total_depots': total_depots,
            'total_retraits': total_retraits,
            'total_transferts': total_transferts,
        }

        
        cache_stats.inserer('transactions', 'global', donnees)

        serializer = NbrtransactionsSerializer(donnees)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListeDepotsAttenteView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        depots_en_attente = Depots.objects.filter(
            status='en_attente'
        ).select_related('id_utilisateur__user')

        data = []
        for depot in depots_en_attente:
            utilisateur = depot.id_utilisateur
            data.append({
                'id_depot': depot.id_depot,
                'nom_utilisateur': utilisateur.user.username,
                'telephone': utilisateur.telephone,
                'montant': depot.montant,
                'status': depot.status,
                'date_demande': depot.date_demande,
            })

        
        alertes = [{'type': 'depot_en_attente', 'montant': d['montant'],
                    'date_creation': d['date_demande'], 'id': d['id_depot']} for d in data]
        alertes_ordonnees = ordonner_alertes_admin(alertes)
        ids_ordonnes = [a['id'] for a in alertes_ordonnees]
        data_map = {d['id_depot']: d for d in data}
        data_ordonnee = [data_map[i] for i in ids_ordonnes if i in data_map]

        serializer = ListeDepotsAttenteSerializer(data_ordonnee, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListeRetraitsAttenteView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        retraits_en_attente = Retrait.objects.filter(
            status='en_attente'
        ).select_related('id_utilisateur__user')

        data = []
        for retrait in retraits_en_attente:
            utilisateur = retrait.id_utilisateur
            data.append({
                'id_retrait': retrait.id_retrait,
                'nom_utilisateur': utilisateur.user.username,
                'telephone': utilisateur.telephone,
                'montant': retrait.montant,
                'status': retrait.status,
                'date_demande': retrait.date_demande,
            })

        
        alertes = [{'type': 'retrait_en_attente', 'montant': r['montant'],
                    'date_creation': r['date_demande'], 'id': r['id_retrait']} for r in data]
        alertes_ordonnees = ordonner_alertes_admin(alertes)
        ids_ordonnes = [a['id'] for a in alertes_ordonnees]
        data_map = {r['id_retrait']: r for r in data}
        data_ordonnee = [data_map[i] for i in ids_ordonnes if i in data_map]

        serializer = ListeRetraitsAttenteSerializer(data_ordonnee, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopCommercantsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        k = int(request.query_params.get('k', 10))

        top_commercants_raw = PaiementsCommercants.objects.values(
            nom_commercant=F('id_commercant__user__username'),
            nom_boutique=F('id_commercant__commercant__nom_boutique'),
            telephone=F('id_commercant__telephone'),
        ).annotate(
            total_recu=Sum('montant'),
            nombre_paiements=Count('id_paiement')
        ).order_by('-total_recu')

        
        stats_list = [
            {
                'id_commercant': i,
                'nom_boutique': c.get('nom_boutique', ''),
                'nom_commercant': c.get('nom_commercant', ''),
                'telephone': c.get('telephone', ''),
                'total_recu': float(c.get('total_recu') or 0),
                'nombre_paiements': c.get('nombre_paiements', 0),
                'volume_total': float(c.get('total_recu') or 0),
            }
            for i, c in enumerate(top_commercants_raw)
        ]
        top = top_k_multi_criteres(stats_list, k=k, critere='volume')

        
        for c in top:
            top_commercants_heap.ajouter_ou_mettre_a_jour(
                c.get('id_commercant', 0),
                c.get('total_recu', 0),
                {'nom_boutique': c.get('nom_boutique', ''), 'telephone': c.get('telephone', '')},
            )

        serializer = TopCommercantsSerializer(top, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopUtilisateursView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        k = int(request.query_params.get('k', 10))

        top_utilisateurs_raw = Transactions.objects.filter(
            type_transaction='transfert'
        ).values(
            nom_utilisateur=F('id_expediteur__user__username'),
            telephone=F('id_expediteur__telephone'),
        ).annotate(
            total_envoye=Sum('montant'),
            nombre_transactions=Count('id_transaction')
        ).order_by('-total_envoye')

        
        stats_list = [
            {
                'id_utilisateur': i,
                'nom_utilisateur': u.get('nom_utilisateur', ''),
                'telephone': u.get('telephone', ''),
                'total_envoye': float(u.get('total_envoye') or 0),
                'nombre_transactions': u.get('nombre_transactions', 0),
                'volume_total': float(u.get('total_envoye') or 0),
            }
            for i, u in enumerate(top_utilisateurs_raw)
        ]
        top = top_k_multi_criteres(stats_list, k=k, critere='volume')

        
        for u in top:
            top_utilisateurs_heap.ajouter_ou_mettre_a_jour(
                u.get('id_utilisateur', 0),
                u.get('total_envoye', 0),
                {'nom_utilisateur': u.get('nom_utilisateur', ''), 'telephone': u.get('telephone', '')},
            )

        serializer = TopUtilisateursSerializer(top, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionsParPeriodeView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        type_periode = request.query_params.get('type_periode', 'jour')

        if type_periode == 'jour':
            trunc_func = TruncDay('date_transaction')
        elif type_periode == 'semaine':
            trunc_func = TruncWeek('date_transaction')
        elif type_periode == 'mois':
            trunc_func = TruncMonth('date_transaction')
        else:
            return Response(
                {"detail": "Type invalide. Utilisez 'jour', 'semaine' ou 'mois'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        transactions_par_periode = Transactions.objects.annotate(
            periode_date=trunc_func
        ).values('periode_date').annotate(
            nombre_transactions=Count('id_transaction'),
            volume_total=Sum('montant')
        ).order_by('periode_date')

        data = []
        for item in transactions_par_periode:
            periode_date = item['periode_date']
            if periode_date:
                periode_str = str(periode_date.date())
                nb = item['nombre_transactions']
                vol = float(item['volume_total'] or 0)

                data.append({
                    'periode': periode_str,
                    'nombre_transactions': nb,
                    'volume_total': vol,
                    'type_periode': type_periode,
                })

                
                avl_periodes.inserer(periode_date.date(), nb, vol)
                cache_stats.inserer(f'periode_{type_periode}', periode_str,
                                    {'nb': nb, 'volume': vol})

                
                graphe_global.enregistrer_flux('transactions', type_periode, vol, nb)

        serializer = TransactionsParPeriodeSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionsSuspectesView(APIView):
    """[ALGO] Analyse et classification des transactions suspectes."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        seuil_haut = float(request.query_params.get('seuil_haut', 1_000_000))
        seuil_freq = int(request.query_params.get('seuil_freq', 20))

        transactions = Transactions.objects.all()
        trans_list = [
            {
                'id_transaction': t.id_transaction,
                'montant': float(t.montant),
                'id_expediteur': t.id_expediteur.id_utilisateur,
                'type_transaction': t.type_transaction,
                'date_transaction': t.date_transaction,
            }
            for t in transactions
        ]

        suspectes = analyser_transactions_batch(trans_list, seuil_haut, seuil_freq)
        return Response({
            'nb_suspectes': len(suspectes),
            'transactions': suspectes,
        }, status=status.HTTP_200_OK)


class MetriquesDashboardView(APIView):
    """[ALGO] Sélection gloutonne des métriques à afficher selon un quota."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        quota = int(request.query_params.get('quota', 15))
        metriques = selectionner_metriques_greedy(quota_calcul=quota)
        return Response({
            'metriques_selectionnees': metriques,
            'quota_utilise': quota,
        }, status=status.HTTP_200_OK)


class StatsRangeView(APIView):
    """[DS] Statistiques par plage de dates via l'arbre AVL."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from datetime import date
        debut_str = request.query_params.get('debut')
        fin_str = request.query_params.get('fin')

        if not debut_str or not fin_str:
            return Response(
                {"detail": "Paramètres 'debut' et 'fin' requis (format YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            debut = date.fromisoformat(debut_str)
            fin = date.fromisoformat(fin_str)
        except ValueError:
            return Response({"detail": "Format de date invalide."}, status=status.HTTP_400_BAD_REQUEST)

        
        stats = avl_periodes.stats_entre(debut, fin)

        if not stats:
            
            from django.db.models.functions import TruncDay
            from django.db.models import Sum, Count
            from datetime import datetime
            debut_dt = datetime.combine(debut, datetime.min.time())
            fin_dt = datetime.combine(fin, datetime.max.time())
            qs = Transactions.objects.filter(
                date_transaction__range=(debut_dt, fin_dt)
            ).annotate(jour=TruncDay('date_transaction')).values('jour').annotate(
                nb=Count('id_transaction'), volume=Sum('montant')
            )
            stats = [
                {'date': str(r['jour'].date()), 'nb': r['nb'], 'volume': float(r['volume'] or 0)}
                for r in qs
            ]

        return Response({'debut': debut_str, 'fin': fin_str, 'stats': stats}, status=status.HTTP_200_OK)
