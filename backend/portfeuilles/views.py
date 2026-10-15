from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
import uuid
from transaction.models import Transactions
from portfeuilles.models import Portefeuilles
from portfeuilles.serializers import PortefeuilleSerializer, TransfertSerializer


from portfeuilles.data_structures import cache_portefeuilles, file_transferts, graphe_flux
from portfeuilles.algorithms import (
    valider_transfert,
    ordonner_transferts,
    top_k_portefeuilles_actifs,
    optimiser_transferts_greedy,
)


class SoldeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        utilisateur = request.user.utilisateur

        
        cached = cache_portefeuilles.solde(utilisateur.id_utilisateur)
        if cached is not None:
            return Response({'solde': str(cached)}, status=status.HTTP_200_OK)

        try:
            portefeuille = Portefeuilles.objects.get(id_utilisateur=utilisateur)
        except Portefeuilles.DoesNotExist:
            return Response({"detail": "Portefeuille non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        
        cache_portefeuilles.inserer(
            utilisateur.id_utilisateur,
            portefeuille.id_portefeuille,
            portefeuille.solde
        )

        serializer = PortefeuilleSerializer(portefeuille)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransfertArgentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransfertSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        telephone_destinataire = serializer.validated_data['telephone_destinataire']
        montant = serializer.validated_data['montant']

        try:
            with transaction.atomic():
                p_source_id = Portefeuilles.objects.get(id_utilisateur=request.user.utilisateur).id_portefeuille
                p_dest_id = Portefeuilles.objects.get(id_utilisateur__telephone=telephone_destinataire).id_portefeuille

                ids_tries = sorted([p_source_id, p_dest_id])
                verrouilles = Portefeuilles.objects.select_for_update().filter(
                    id_portefeuille__in=ids_tries
                ).order_by('id_portefeuille')

                dico_portefeuilles = {p.id_portefeuille: p for p in verrouilles}
                portefeuille_source = dico_portefeuilles[p_source_id]
                portefeuille_destinataire = dico_portefeuilles[p_dest_id]

                
                expediteur_actif = request.user.utilisateur.statut_compte == 'actif'
                dest_utilisateur = portefeuille_destinataire.id_utilisateur
                destinataire_actif = dest_utilisateur.statut_compte == 'actif'
                solde_suffisant = portefeuille_source.solde >= montant

                resultat, motif = valider_transfert(
                    expediteur_actif=expediteur_actif,
                    destinataire_actif=destinataire_actif,
                    solde_suffisant=solde_suffisant,
                )

                if resultat != 'VALIDE':
                    return Response({"detail": motif}, status=status.HTTP_400_BAD_REQUEST)

                portefeuille_source.solde -= montant
                portefeuille_destinataire.solde += montant
                portefeuille_source.save()
                portefeuille_destinataire.save()

                
                cache_portefeuilles.mettre_a_jour_solde(
                    request.user.utilisateur.id_utilisateur,
                    portefeuille_source.solde
                )
                cache_portefeuilles.mettre_a_jour_solde(
                    dest_utilisateur.id_utilisateur,
                    portefeuille_destinataire.solde
                )

                ref = str(uuid.uuid4()).replace('-', '').upper()[:20]
                Transactions.objects.create(
                    type_transaction='transfert',
                    montant=montant,
                    id_expediteur=portefeuille_source.id_utilisateur,
                    id_destinataire=portefeuille_destinataire.id_utilisateur,
                    reference=ref,
                    status='validee'
                )

                
                graphe_flux.enregistrer_transfert(p_source_id, p_dest_id, float(montant))

        except Portefeuilles.DoesNotExist:
            return Response({"detail": "Portefeuille source ou destinataire non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Transfert effectué avec succès."}, status=status.HTTP_200_OK)


class TopPortefeuillesView(APIView):
    """[ALGO] Top-k des portefeuilles les plus actifs."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        k = int(request.query_params.get('k', 10))
        portefeuilles = Portefeuilles.objects.all()

        stats = []
        for p in portefeuilles:
            volume_sortant = graphe_flux.flux_sortant_total(p.id_portefeuille)
            volume_entrant = graphe_flux.flux_entrant_total(p.id_portefeuille)
            stats.append({
                'id_portefeuille': p.id_portefeuille,
                'id_utilisateur': p.id_utilisateur.id_utilisateur,
                'username': p.id_utilisateur.user.username,
                'solde': float(p.solde),
                'volume_total': volume_sortant + volume_entrant,
            })

        top = top_k_portefeuilles_actifs(stats, k=k)
        return Response(top, status=status.HTTP_200_OK)


class CyclesSuspectsView(APIView):
    """[DS] Détection de cycles suspects dans le graphe de flux."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        portefeuilles = Portefeuilles.objects.all()
        cycles = []
        for p in portefeuilles:
            if graphe_flux.detecter_cycle(p.id_portefeuille):
                cycles.append({
                    'id_portefeuille': p.id_portefeuille,
                    'username': p.id_utilisateur.user.username,
                    'flux_sortant': graphe_flux.flux_sortant_total(p.id_portefeuille),
                })
        return Response({'cycles_detectes': cycles, 'nb': len(cycles)}, status=status.HTTP_200_OK)
