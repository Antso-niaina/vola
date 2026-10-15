from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import timedelta
import random

from compte.models import Utilisateurs, Client, Commercant, Authentification, Journaux, Admin
from portfeuilles.models import Portefeuilles
from authentification.serializers import (
    InscriptionSerializer,
    ConnexionSerializer,
    OTPSerializer,
    DeconnexionSerializer,
    ChangerMotDePasseSerializer,
    AttribuerRoleAdminSerializer,
    ListeUtilisateursSerializer,
    ModifierPermissionsAdminSerializer
)
from authentification.models import TentativeConnexion


from authentification.data_structures import otp_cache, tentative_heap, graphe_sessions
from authentification.algorithms import (
    selectionner_meilleur_otp,
    valider_connexion,
    top_k_ips_suspectes,
    ordonner_tentatives_suspectes,
)


class InscriptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
            )

            if data['role'] == 'client':
                utilisateur = Client.objects.create(
                    user=user,
                    telephone=data['telephone'],
                    role=data['role'],
                    photo_identite=data.get('photo_identite', None),
                )
            elif data['role'] == 'commercant':
                utilisateur = Commercant.objects.create(
                    user=user,
                    telephone=data['telephone'],
                    role=data['role'],
                    photo_identite=data.get('photo_identite', None),
                    nom_boutique=data['nom_boutique'],
                    adresse=data.get('adresse', ''),
                )
            else:
                utilisateur = Utilisateurs.objects.create(
                    user=user,
                    telephone=data['telephone'],
                    role=data['role'],
                    photo_identite=data.get('photo_identite', None),
                )

            Portefeuilles.objects.create(
                id_utilisateur=utilisateur,
                solde=0.00
            )

            Journaux.objects.create(
                id_utilisateur=utilisateur,
                action=f"Inscription de {user.username} en tant que {data['role']}"
            )

            
            graphe_sessions.ajouter_utilisateur(utilisateur.id_utilisateur)

        return Response({
            'message': 'Compte créé avec succès.',
            'username': user.username,
            'role': data['role'],
        }, status=status.HTTP_201_CREATED)


class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConnexionSerializer(data=request.data)
        if not serializer.is_valid():
            username = request.data.get('username', '')
            user = User.objects.filter(username=username).first()
            utilisateur = getattr(user, 'utilisateur', None) if user else None

            
            import time
            tentative_heap.ajouter(
                timestamp=time.time(),
                telephone=utilisateur.telephone if utilisateur else username,
                ip=request.META.get('REMOTE_ADDR', ''),
                type_tentative='login',
                succes=False,
            )

            TentativeConnexion.objects.create(
                id_utilisateur=utilisateur,
                type_tentative='login',
                telephone=utilisateur.telephone if utilisateur else username,
                ip_address=request.META.get('REMOTE_ADDR'),
                succes=False
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        utilisateur = user.utilisateur

        code_otp = str(random.randint(100000, 999999))
        print(f"Code OTP généré : {code_otp}")
        expiration = timezone.now() + timedelta(minutes=5)

        
        Authentification.objects.filter(
            id_utilisateur=utilisateur,
            utilise=False
        ).update(utilise=True)

        
        otp_cache.marquer_utilise(utilisateur.telephone)

        Authentification.objects.create(
            id_utilisateur=utilisateur,
            code_otp=code_otp,
            expiration=expiration,
            utilise=False
        )

        
        otp_cache.inserer(utilisateur.telephone, code_otp, expiration)

        import time
        tentative_heap.ajouter(
            timestamp=time.time(),
            telephone=utilisateur.telephone,
            ip=request.META.get('REMOTE_ADDR', ''),
            type_tentative='login',
            succes=True,
        )

        TentativeConnexion.objects.create(
            id_utilisateur=utilisateur,
            type_tentative='login',
            telephone=utilisateur.telephone,
            ip_address=request.META.get('REMOTE_ADDR'),
            succes=True
        )

        Journaux.objects.create(
            id_utilisateur=utilisateur,
            action=f"Identifiants valides pour {user.username} - OTP envoyé"
        )

        response_data = {
            'message': 'Code OTP envoyé.',
            'username': user.username,
        }
        if settings.DEBUG:
            response_data['otp_dev'] = code_otp

        return Response(response_data, status=status.HTTP_200_OK)


class VerifierOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        user_for_check = User.objects.filter(username=username).first()
        utilisateur_for_check = getattr(user_for_check, 'utilisateur', None) if user_for_check else None

        
        import time
        fenetre_debut = time.time() - 300  
        failed_attempts_heap = 0
        if utilisateur_for_check:
            failed_attempts_heap = tentative_heap.compter_echecs_recents(
                telephone=utilisateur_for_check.telephone,
                depuis_timestamp=fenetre_debut,
                type_tentative='otp',
            )

        
        if utilisateur_for_check and failed_attempts_heap == 0:
            window_start = timezone.now() - timedelta(minutes=5)
            failed_attempts_heap = TentativeConnexion.objects.filter(
                id_utilisateur=utilisateur_for_check,
                type_tentative='otp',
                succes=False,
                date_tentative__gte=window_start
            ).count()

        if failed_attempts_heap >= 5:
            return Response({
                'error': 'Trop de tentatives. Réessayez dans quelques minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        
        code_fourni = request.data.get('code_otp', '')
        telephone = utilisateur_for_check.telephone if utilisateur_for_check else ''
        otp_cache_valide = otp_cache.est_valide(telephone, code_fourni) if telephone else False

        serializer = OTPSerializer(data=request.data)
        if not serializer.is_valid():
            tentative_heap.ajouter(
                timestamp=time.time(),
                telephone=telephone,
                ip=request.META.get('REMOTE_ADDR', ''),
                type_tentative='otp',
                succes=False,
            )
            TentativeConnexion.objects.create(
                id_utilisateur=utilisateur_for_check,
                type_tentative='otp',
                telephone=telephone or username,
                ip_address=request.META.get('REMOTE_ADDR'),
                succes=False
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']
        utilisateur = user.utilisateur

        
        compte_actif = utilisateur.statut_compte == 'actif'
        nb_echecs = tentative_heap.compter_echecs_recents(
            telephone=utilisateur.telephone,
            depuis_timestamp=fenetre_debut,
            type_tentative='otp',
        )
        resultat_arbre, motif_arbre = valider_connexion(
            compte_actif=compte_actif,
            nb_echecs_recents=nb_echecs,
            otp_valide=True,
        )

        if resultat_arbre != 'SUCCES':
            return Response({'error': motif_arbre},
                            status=status.HTTP_403_FORBIDDEN)

        
        otp_obj.utilise = True
        otp_obj.save()

        
        otp_cache.marquer_utilise(utilisateur.telephone)

        tentative_heap.ajouter(
            timestamp=time.time(),
            telephone=utilisateur.telephone,
            ip=request.META.get('REMOTE_ADDR', ''),
            type_tentative='otp',
            succes=True,
        )

        TentativeConnexion.objects.create(
            id_utilisateur=utilisateur,
            type_tentative='otp',
            telephone=utilisateur.telephone,
            ip_address=request.META.get('REMOTE_ADDR'),
            succes=True
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        
        graphe_sessions.ajouter_session(
            id_utilisateur=utilisateur.id_utilisateur,
            jti=str(refresh.access_token['jti']),
            ip=request.META.get('REMOTE_ADDR', ''),
            date_creation=timezone.now(),
        )

        Journaux.objects.create(
            id_utilisateur=utilisateur,
            action=f"OTP vérifié - connexion complète de {user.username}"
        )

        return Response({
            'message': 'Connexion réussie.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'role': utilisateur.role,
            'username': user.username,
        }, status=status.HTTP_200_OK)


class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeconnexionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(serializer.validated_data['refresh_token'])
            token.blacklist()

            utilisateur = request.user.utilisateur

            
            graphe_sessions.revoquer_toutes(utilisateur.id_utilisateur)

            Journaux.objects.create(
                id_utilisateur=utilisateur,
                action=f"Déconnexion de {request.user.username}"
            )

            return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user

        if not user.check_password(data['ancien_mot_de_passe']):
            return Response({'error': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['nouveau_mot_de_passe'])
        user.save()

        utilisateur = user.utilisateur
        Journaux.objects.create(
            id_utilisateur=utilisateur,
            action=f"Changement de mot de passe de {user.username}"
        )

        return Response({'message': 'Mot de passe changé avec succès.'}, status=status.HTTP_200_OK)


class ListeUtilisateursView(APIView):
    """View pour lister tous les utilisateurs (admin only)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            utilisateur = request.user.utilisateur
            if utilisateur.role != 'admin':
                return Response(
                    {'error': 'Vous n\'avez pas la permission d\'accéder à cette ressource.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Utilisateurs.DoesNotExist:
            return Response({'error': 'Profil utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        
        utilisateurs = Utilisateurs.objects.all()
        serializer = ListeUtilisateursSerializer(utilisateurs, many=True)

        Journaux.objects.create(
            id_utilisateur=utilisateur,
            action=f"Consultation de la liste des utilisateurs"
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class AttribuerRoleAdminView(APIView):
    """View pour attribuer un rôle d'administrateur à un utilisateur"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        try:
            utilisateur = request.user.utilisateur
            if utilisateur.role != 'admin':
                return Response(
                    {'error': 'Vous n\'avez pas la permission d\'effectuer cette action.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Utilisateurs.DoesNotExist:
            return Response({'error': 'Profil utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttribuerRoleAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        utilisateur_cible = serializer.validated_data['utilisateur']

        with transaction.atomic():
            
            utilisateur_cible.role = 'admin'
            utilisateur_cible.save()

            
            if not hasattr(utilisateur_cible, 'admin'):
                admin_obj = Admin(
                    utilisateurs_ptr_id=utilisateur_cible.id_utilisateur,
                    peut_valider_depot=True,
                    peut_valider_retrait=True,
                    peut_bloquer_utilisateur=True,
                )
                admin_obj.__dict__.update(utilisateur_cible.__dict__)
                admin_obj.save()

                utilisateur_cible.user.is_staff = True
                utilisateur_cible.user.save()

            Journaux.objects.create(
                id_utilisateur=utilisateur,
                action=f"Attribution du rôle admin à {utilisateur_cible.user.username}"
            )

        return Response({
            'message': f'Rôle administrateur attribué à {utilisateur_cible.user.username}.',
            'utilisateur': ListeUtilisateursSerializer(utilisateur_cible).data
        }, status=status.HTTP_200_OK)


class ModifierPermissionsAdminView(APIView):
    """View pour modifier les permissions d'un administrateur"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        
        try:
            utilisateur = request.user.utilisateur
            if utilisateur.role != 'admin':
                return Response(
                    {'error': 'Vous n\'avez pas la permission d\'effectuer cette action.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Utilisateurs.DoesNotExist:
            return Response({'error': 'Profil utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ModifierPermissionsAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        utilisateur_cible = serializer.validated_data['utilisateur']
        data = serializer.validated_data

        try:
            
            admin_obj = Admin.objects.get(id_utilisateur=utilisateur_cible.id_utilisateur)

            
            if 'peut_valider_depot' in data:
                admin_obj.peut_valider_depot = data['peut_valider_depot']
            if 'peut_valider_retrait' in data:
                admin_obj.peut_valider_retrait = data['peut_valider_retrait']
            if 'peut_bloquer_utilisateur' in data:
                admin_obj.peut_bloquer_utilisateur = data['peut_bloquer_utilisateur']

            admin_obj.save()

            Journaux.objects.create(
                id_utilisateur=utilisateur,
                action=f"Modification des permissions de l'administrateur {utilisateur_cible.user.username}"
            )

            return Response({
                'message': 'Permissions modifiées avec succès.',
                'permissions': {
                    'peut_valider_depot': admin_obj.peut_valider_depot,
                    'peut_valider_retrait': admin_obj.peut_valider_retrait,
                    'peut_bloquer_utilisateur': admin_obj.peut_bloquer_utilisateur,
                }
            }, status=status.HTTP_200_OK)

        except Admin.DoesNotExist:
            return Response(
                {'error': 'Cet utilisateur n\'a pas encore de profil administrateur.'},
                status=status.HTTP_404_NOT_FOUND
            )
