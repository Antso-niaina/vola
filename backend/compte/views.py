from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import timedelta
import random

from compte.models import Utilisateurs,Admin, Journaux
from portfeuilles.models import Portefeuilles
from compte.serializers import (
    ClientSerializer,
    CommercantSerializer,
    AdminSerializer,
    UtilisateurUpdateSerializer,
    AttribuerRoleAdminSerializer,
    ModifierPermissionsAdminSerializer
)

class ProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            utilisateur = request.user.utilisateur
        except Utilisateurs.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        if utilisateur.role == 'client':
            serializer = ClientSerializer(utilisateur)
        elif utilisateur.role == 'commercant':
            serializer = CommercantSerializer(utilisateur)
        elif utilisateur.role == 'admin':
            serializer = AdminSerializer(utilisateur)
        else:
            return Response(
                {"detail": "Rôle d'utilisateur inconnu."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)
class UpdateProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            utilisateur = request.user.utilisateur
        except Utilisateurs.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer_update = UtilisateurUpdateSerializer(
            utilisateur, data=request.data, partial=True
        )
        if not serializer_update.is_valid():
            return Response(serializer_update.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer_update.save()

        
        if utilisateur.role == 'commercant' and hasattr(utilisateur, 'commercant'):
            nom_boutique = request.data.get('nom_boutique')
            if nom_boutique:
                utilisateur.commercant.nom_boutique = nom_boutique
                utilisateur.commercant.save()

        if utilisateur.role == 'client':
            serializer = ClientSerializer(utilisateur)
        elif utilisateur.role == 'commercant':
            serializer = CommercantSerializer(utilisateur)
        elif utilisateur.role == 'admin':
            serializer = AdminSerializer(utilisateur)
        else:
            return Response(
                {"detail": "Rôle d'utilisateur inconnu."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

class ListeUtilisateursView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        utilisateurs = Utilisateurs.objects.all()
        data = []
        for utilisateur in utilisateurs:
            if utilisateur.role == 'client':
                serializer = ClientSerializer(utilisateur)
            elif utilisateur.role == 'commercant':
                serializer = CommercantSerializer(utilisateur)
            elif utilisateur.role == 'admin':
                serializer = AdminSerializer(utilisateur)
            else:
                continue
            data.append(serializer.data)

        return Response(data, status=status.HTTP_200_OK)

class AttribuerRoleAdminView(APIView):
    """Attribuer le rôle admin à un utilisateur existant"""
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AttribuerRoleAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            utilisateur = Utilisateurs.objects.get(
                id_utilisateur=data['id_utilisateur']
            )
        except Utilisateurs.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            ancien_role = utilisateur.role
            date_creation = utilisateur.date_creation
            
            if ancien_role != 'admin':
                if ancien_role == 'client' and hasattr(utilisateur, 'client'):
                    utilisateur.client.delete(keep_parents=True)
                    date_creation.client.delete(keep_parents=True)
                elif ancien_role == 'commercant' and hasattr(utilisateur, 'commercant'):
                    utilisateur.commercant.delete(keep_parents=True)
                    date_creation.commercant.delete(keep_parents=True)

            
            utilisateur.role = 'admin'
            utilisateur.date_creation = date_creation(auto_now_add=True)
            utilisateur.save()

            
            if not hasattr(utilisateur, 'admin'):
                admin_obj = Admin(
                    utilisateurs_ptr_id=utilisateur.id_utilisateur,
                    peut_valider_depot=data['peut_valider_depot'],
                    peut_valider_retrait=data['peut_valider_retrait'],
                    peut_bloquer_utilisateur=data['peut_bloquer_utilisateur'],
                )
                admin_obj.__dict__.update(utilisateur.__dict__)
                admin_obj.save()

            
            utilisateur.user.is_staff = True
            utilisateur.user.save()

            
            admin = request.user.utilisateur
            Journaux.objects.create(
                id_utilisateur=admin,
                action=f"{utilisateur.user.username} promu admin depuis {ancien_role} par {admin.user.username}"
            )

        return Response({
            "detail": f"{utilisateur.user.username} est maintenant admin.",
            "permissions": {
                "peut_valider_depot": data['peut_valider_depot'],
                "peut_valider_retrait": data['peut_valider_retrait'],
                "peut_bloquer_utilisateur": data['peut_bloquer_utilisateur'],
            }
        }, status=status.HTTP_201_CREATED)


class ModifierPermissionsAdminView(APIView):
    """Modifier les permissions d'un admin existant"""
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        try:
            utilisateur = Utilisateurs.objects.get(id_utilisateur=id)
        except Utilisateurs.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        if utilisateur.role != 'admin':
            return Response(
                {"detail": "Cet utilisateur n'est pas admin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ModifierPermissionsAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not hasattr(utilisateur, 'admin'):
            return Response(
                {"detail": "Profil admin introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        profil_admin = utilisateur.admin

        
        if 'peut_valider_depot' in data:
            profil_admin.peut_valider_depot = data['peut_valider_depot']
        if 'peut_valider_retrait' in data:
            profil_admin.peut_valider_retrait = data['peut_valider_retrait']
        if 'peut_bloquer_utilisateur' in data:
            profil_admin.peut_bloquer_utilisateur = data['peut_bloquer_utilisateur']

        profil_admin.save()

        
        admin = request.user.utilisateur
        Journaux.objects.create(
            id_utilisateur=admin,
            action=f"Permissions de {utilisateur.user.username} modifiées par {admin.user.username}"
        )

        return Response({
            "detail": "Permissions mises à jour.",
            "utilisateur": utilisateur.user.username,
            "permissions": {
                "peut_valider_depot": profil_admin.peut_valider_depot,
                "peut_valider_retrait": profil_admin.peut_valider_retrait,
                "peut_bloquer_utilisateur": profil_admin.peut_bloquer_utilisateur,
            }
        }, status=status.HTTP_200_OK)