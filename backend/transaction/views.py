from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import timedelta
import random
import uuid
from transaction.models import Transactions
from portfeuilles.models import Portefeuilles
from transaction.models import Depots, Retrait
from transaction.serializers import (
    TransactionSerializer, EnvoiArgentSerializer, DepotSerializer, RetraitSerializer,
    DemandeDepotSerializer, DemandeRetraitSerializer
)


from transaction.data_structures import (
    index_references, file_admin, graphe_transactions, avl_montants
)
from transaction.algorithms import (
    ordonner_validations,
    valider_depot,
    valider_retrait,
    top_k_transactions_montant,
    selectionner_demandes_greedy,
)


class TransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transactions.objects.filter(
            id_expediteur=request.user.utilisateur
        ) | Transactions.objects.filter(
            id_destinataire=request.user.utilisateur
        )
        transactions = transactions.order_by('-date_transaction')

        
        for t in transactions:
            if not index_references.existe(t.reference):
                index_references.inserer(t.reference, {
                    'id': t.id_transaction,
                    'type': t.type_transaction,
                    'montant': float(t.montant),
                    'status': t.status,
                })

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DepotAdminAttentView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        depots_en_attente = Depots.objects.filter(status='en_attente')

        
        depots_list = list(depots_en_attente)
        depots_dicts = [
            {
                'id': d.id_depot, 'type': 'depot',
                'montant': d.montant,
                'date_demande': d.date_demande,
            }
            for d in depots_list
        ]
        depots_dicts_ordonnes = ordonner_validations(depots_dicts)

        
        id_to_obj = {d.id_depot: d for d in depots_list}
        depots_ordonnes = [id_to_obj[d['id']] for d in depots_dicts_ordonnes if d['id'] in id_to_obj]

        
        for d in depots_list:
            file_admin.ajouter_depot(d.id_depot, d.id_utilisateur.id_utilisateur,
                                     d.montant, d.date_demande)

        serializer = DepotSerializer(depots_ordonnes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ValidationDepotView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id_depot):
        try:
            depot = Depots.objects.get(id_depot=id_depot, status='en_attente')
        except Depots.DoesNotExist:
            return Response(
                {"detail": "Demande de dépôt non trouvée ou déjà traitée."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        admin_util = request.user.utilisateur
        admin_peut_valider = getattr(getattr(admin_util, 'admin', None), 'peut_valider_depot', True)
        montant_valide = depot.montant > 0

        resultat, motif = valider_depot(
            admin_peut_valider=admin_peut_valider,
            depot_en_attente=True,
            montant_valide=montant_valide,
        )

        if resultat != 'VALIDE':
            return Response({"detail": motif}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            depot.status = 'validee'
            depot.id_admin = request.user.utilisateur
            depot.date_validation = timezone.now()
            depot.save()

            portefeuille = Portefeuilles.objects.select_for_update().get(id_utilisateur=depot.id_utilisateur)
            portefeuille.solde += depot.montant
            portefeuille.save()

            ref = str(uuid.uuid4()).replace('-', '').upper()[:20]
            t = Transactions.objects.create(
                type_transaction='depot',
                montant=depot.montant,
                id_expediteur=depot.id_utilisateur,
                id_destinataire=depot.id_utilisateur,
                reference=ref,
                status='validee'
            )

            
            index_references.inserer(ref, {
                'id': t.id_transaction, 'type': 'depot',
                'montant': float(depot.montant), 'status': 'validee',
            })
            
            avl_montants.inserer(float(depot.montant), t.id_transaction)

        return Response({"detail": "Dépôt validé et solde mis à jour."}, status=status.HTTP_200_OK)


class RefusDepotView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id_depot):
        try:
            depot = Depots.objects.get(id_depot=id_depot, status='en_attente')
        except Depots.DoesNotExist:
            return Response(
                {"detail": "Demande de dépôt non trouvée ou déjà traitée."},
                status=status.HTTP_404_NOT_FOUND
            )

        depot.status = 'refusee'
        depot.id_admin = request.user.utilisateur
        depot.date_validation = timezone.now()
        depot.save()

        return Response({"detail": "Dépôt refusé."}, status=status.HTTP_200_OK)


class RetraitAdminAttentView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        retraits_en_attente = Retrait.objects.filter(status='en_attente')

        retraits_list = list(retraits_en_attente)
        retraits_dicts = [
            {
                'id': r.id_retrait, 'type': 'retrait',
                'montant': r.montant,
                'date_demande': r.date_demande,
            }
            for r in retraits_list
        ]
        retraits_dicts_ordonnes = ordonner_validations(retraits_dicts)

        id_to_obj = {r.id_retrait: r for r in retraits_list}
        retraits_ordonnes = [id_to_obj[r['id']] for r in retraits_dicts_ordonnes if r['id'] in id_to_obj]

        for r in retraits_list:
            file_admin.ajouter_retrait(r.id_retrait, r.id_utilisateur.id_utilisateur,r.montant, r.date_demande)

        serializer = RetraitSerializer(retraits_ordonnes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ValidationRetraitView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id_retrait):
        try:
            retrait = Retrait.objects.get(id_retrait=id_retrait, status='en_attente')
        except Retrait.DoesNotExist:
            return Response(
                {"detail": "Demande de retrait non trouvée ou déjà traitée."},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            portefeuille = Portefeuilles.objects.select_for_update().get(id_utilisateur=retrait.id_utilisateur)
            solde_suffisant = portefeuille.solde >= retrait.montant

            admin_util = request.user.utilisateur
            admin_peut_valider = getattr(getattr(admin_util, 'admin', None), 'peut_valider_retrait', True)

            resultat, motif = valider_retrait(
                admin_peut_valider=admin_peut_valider,
                retrait_en_attente=True,
                solde_suffisant=solde_suffisant,
            )

            if resultat != 'VALIDE':
                return Response({"detail": motif}, status=status.HTTP_400_BAD_REQUEST)

            portefeuille.solde -= retrait.montant
            portefeuille.save()

            retrait.status = 'validee'
            retrait.id_admin = request.user.utilisateur
            retrait.date_validation = timezone.now()
            retrait.save()

            ref = str(uuid.uuid4()).replace('-', '').upper()[:20]
            t = Transactions.objects.create(
                type_transaction='retrait',
                montant=retrait.montant,
                id_expediteur=retrait.id_utilisateur,
                id_destinataire=retrait.id_utilisateur,
                reference=ref,
                status='validee'
            )

            index_references.inserer(ref, {
                'id': t.id_transaction, 'type': 'retrait',
                'montant': float(retrait.montant), 'status': 'validee',
            })
            avl_montants.inserer(float(retrait.montant), t.id_transaction)

        return Response({"detail": "Retrait validé et solde mis à jour."}, status=status.HTTP_200_OK)


class RefusRetraitView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id_retrait):
        try:
            retrait = Retrait.objects.get(id_retrait=id_retrait, status='en_attente')
        except Retrait.DoesNotExist:
            return Response(
                {"detail": "Demande de retrait non trouvée ou déjà traitée."},
                status=status.HTTP_404_NOT_FOUND
            )

        retrait.status = 'refusee'
        retrait.id_admin = request.user.utilisateur
        retrait.date_validation = timezone.now()
        retrait.save()

        return Response({"detail": "Retrait refusé."}, status=status.HTTP_200_OK)


class DemandeDepotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DemandeDepotSerializer(data=request.data)
        if serializer.is_valid():
            montant = serializer.validated_data['montant']
            depot = Depots.objects.create(
                id_utilisateur=request.user.utilisateur,
                montant=montant,
                status='en_attente'
            )

            
            file_admin.ajouter_depot(
                depot.id_depot,
                request.user.utilisateur.id_utilisateur,
                montant,
                depot.date_demande,
            )

            return Response(
                {"detail": "Demande de dépôt créée avec succès. En attente de validation."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemandeRetraitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DemandeRetraitSerializer(data=request.data)
        if serializer.is_valid():
            montant = serializer.validated_data['montant']

            try:
                portefeuille = Portefeuilles.objects.get(id_utilisateur=request.user.utilisateur)
                if portefeuille.solde < montant:
                    return Response(
                        {"detail": "Solde insuffisant pour demander ce retrait."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Portefeuilles.DoesNotExist:
                return Response(
                    {"detail": "Portefeuille introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            retrait = Retrait.objects.create(
                id_utilisateur=request.user.utilisateur,
                montant=montant,
                status='en_attente'
            )

            
            file_admin.ajouter_retrait(
                retrait.id_retrait,
                request.user.utilisateur.id_utilisateur,
                montant,
                retrait.date_demande,
            )

            return Response(
                {"detail": "Demande de retrait créée avec succès. En attente de validation."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopTransactionsView(APIView):
    """[ALGO] Top-k des transactions par montant."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        k = int(request.query_params.get('k', 10))
        transactions = Transactions.objects.all()
        trans_list = [
            {
                'id_transaction': t.id_transaction,
                'montant': t.montant,
                'type_transaction': t.type_transaction,
                'date_transaction': t.date_transaction,
            }
            for t in transactions
        ]
        top = top_k_transactions_montant(trans_list, k=k)
        return Response(top, status=status.HTTP_200_OK)


class TransactionsParPlageView(APIView):
    """[DS] Recherche de transactions par plage de montant via AVL."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        min_montant = float(request.query_params.get('min', 0))
        max_montant = float(request.query_params.get('max', 9_999_999))

        
        ids = avl_montants.transactions_dans_plage(min_montant, max_montant)

        if ids:
            transactions = Transactions.objects.filter(id_transaction__in=ids)
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        
        transactions = Transactions.objects.filter(
            montant__gte=min_montant, montant__lte=max_montant
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
