from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
import uuid
from decimal import Decimal, InvalidOperation

from portfeuilles.models import Portefeuilles
from portfeuilles.data_structures import cache_portefeuilles
from commercants.models import QRCode, PaiementsCommercants
from commercants.serializers import QRCodeSerializer, PaiementCommercantSerializer
from compte.models import Journaux


from commercants.data_structures import (
    index_qrcodes, classement_commercants, graphe_paiements, avl_paiements
)
from commercants.algorithms import (
    valider_paiement_qr,
    top_k_commercants_ca,
    ordonner_paiements,
    resoudre_qr_greedy,
)


class GenerateQRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.utilisateur.role != 'commercant':
            return Response(
                {"detail": "Seuls les commerçants peuvent générer un QR code."},
                status=status.HTTP_403_FORBIDDEN
            )

        qr_code, created = QRCode.objects.get_or_create(
            id_commercant=request.user.utilisateur,
            defaults={'code_qr': str(uuid.uuid4())}
        )

        
        nom_boutique = ''
        if hasattr(request.user.utilisateur, 'commercant'):
            nom_boutique = request.user.utilisateur.commercant.nom_boutique
        index_qrcodes.inserer(
            qr_code.code_qr,
            request.user.utilisateur.id_utilisateur,
            nom_boutique,
            actif=True,
        )

        serializer = QRCodeSerializer(qr_code)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class PaiementQrCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code_qr = request.data.get('code_qr')
        montant_str = request.data.get('montant')

        if not code_qr or not montant_str:
            return Response(
                {"detail": "Le code QR et le montant sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            montant = Decimal(str(montant_str))
            if montant <= 0:
                return Response(
                    {"detail": "Le montant doit être strictement positif."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except InvalidOperation:
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)

        
        qr_cached = index_qrcodes.obtenir(code_qr)
        if qr_cached and not qr_cached.get('actif', False):
            return Response({"detail": "Code QR invalide."}, status=status.HTTP_404_NOT_FOUND)

        try:
            qr_code = QRCode.objects.get(code_qr=code_qr)
            commercant = qr_code.id_commercant
        except QRCode.DoesNotExist:
            return Response({"detail": "Code QR invalide."}, status=status.HTTP_404_NOT_FOUND)

        client = request.user.utilisateur

        
        try:
            portefeuille_client = Portefeuilles.objects.get(id_utilisateur=client)
            solde_suffisant = portefeuille_client.solde >= montant
        except Portefeuilles.DoesNotExist:
            solde_suffisant = False

        resultat, motif = valider_paiement_qr(
            qr_valide=True,
            client_different_commercant=(client.id_utilisateur != commercant.id_utilisateur),
            client_actif=(client.statut_compte == 'actif'),
            solde_suffisant=solde_suffisant,
        )

        if resultat != 'VALIDE':
            return Response({"detail": motif}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                p_client_id = Portefeuilles.objects.get(id_utilisateur=client).id_portefeuille
                p_comm_id = Portefeuilles.objects.get(id_utilisateur=commercant).id_portefeuille

                ids_tries = sorted([p_client_id, p_comm_id])
                verrouilles = Portefeuilles.objects.select_for_update().filter(
                    id_portefeuille__in=ids_tries
                ).order_by('id_portefeuille')

                if len(verrouilles) != 2:
                    raise Portefeuilles.DoesNotExist

                dico = {p.id_portefeuille: p for p in verrouilles}
                portefeuille_client_obj = dico[p_client_id]
                portefeuille_commercant = dico[p_comm_id]

                if portefeuille_client_obj.solde < montant:
                    raise ValueError("Solde insuffisant.")

                portefeuille_client_obj.solde -= montant
                portefeuille_commercant.solde += montant
                portefeuille_client_obj.save()
                portefeuille_commercant.save()

                
                cache_portefeuilles.mettre_a_jour_solde(
                    client.id_utilisateur,
                    portefeuille_client_obj.solde
                )
                cache_portefeuilles.mettre_a_jour_solde(
                    commercant.id_utilisateur,
                    portefeuille_commercant.solde
                )

                paiement = PaiementsCommercants.objects.create(
                    id_client=client,
                    id_commercant=commercant,
                    montant=montant,
                    reference=str(uuid.uuid4())
                )

                Journaux.objects.create(
                    id_utilisateur=client,
                    action=f"Paiement de {montant} MGA à {commercant.user.username} — Réf: {paiement.reference}"
                )

                
                graphe_paiements.enregistrer_paiement(
                    client.id_utilisateur, commercant.id_utilisateur, float(montant)
                )
                nom_boutique = commercant.commercant.nom_boutique if hasattr(commercant, 'commercant') else ''
                classement_commercants.ajouter_ou_mettre_a_jour(
                    commercant.id_utilisateur, nom_boutique, float(montant)
                )

                
                avl_paiements.inserer(float(montant), paiement.id_paiement)

            serializer = PaiementCommercantSerializer(paiement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Portefeuilles.DoesNotExist:
            return Response({"detail": "Portefeuille introuvable."}, status=status.HTTP_404_NOT_FOUND)


class HistoriquePaiementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paiements = PaiementsCommercants.objects.filter(
            id_client=request.user.utilisateur
        ).order_by('-date_paiement')
        serializer = PaiementCommercantSerializer(paiements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoriqueRevenusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.utilisateur.role != 'commercant':
            return Response(
                {"detail": "Accès réservé aux commerçants."},
                status=status.HTTP_403_FORBIDDEN
            )

        revenus = PaiementsCommercants.objects.filter(
            id_commercant=request.user.utilisateur
        ).order_by('-date_paiement')
        serializer = PaiementCommercantSerializer(revenus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopCommercantsHeapView(APIView):
    """[DS] Top commerçants via le tas binaire en mémoire (temps réel)."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        n = int(request.query_params.get('n', 10))
        top = classement_commercants.top_n(n=n)
        return Response(top, status=status.HTTP_200_OK)


class PaiementsParPlageView(APIView):
    """[DS] Paiements dans une plage de montant via AVL."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        min_montant = float(request.query_params.get('min', 0))
        max_montant = float(request.query_params.get('max', 9_999_999))

        ids = avl_paiements.paiements_dans_plage(min_montant, max_montant)
        if ids:
            paiements = PaiementsCommercants.objects.filter(id_paiement__in=ids)
        else:
            paiements = PaiementsCommercants.objects.filter(
                montant__gte=min_montant, montant__lte=max_montant
            )

        serializer = PaiementCommercantSerializer(paiements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientsFidelesView(APIView):
    """[DS] Analyse de fidélité client via le graphe de paiements."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.utilisateur.role != 'commercant':
            return Response(
                {"detail": "Accès réservé aux commerçants."},
                status=status.HTTP_403_FORBIDDEN
            )
        commercant_id = request.user.utilisateur.id_utilisateur
        clients_ids = graphe_paiements.clients_du_commercant(commercant_id)
        clients_info = []
        for cid in clients_ids:
            info = graphe_paiements.commercants_du_client(cid).get(commercant_id, {})
            clients_info.append({
                'id_client': cid,
                'montant_total': info.get('montant', 0),
                'nb_paiements': info.get('nb', 0),
            })
        clients_info.sort(key=lambda x: -x['nb_paiements'])
        return Response(clients_info, status=status.HTTP_200_OK)
