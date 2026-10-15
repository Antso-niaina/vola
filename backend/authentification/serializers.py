from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from compte.models import Utilisateurs, Authentification
from authentification.models import TentativeConnexion
from django.utils import timezone
from datetime import timedelta
import random


class InscriptionSerializer(serializers.Serializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    telephone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=['client', 'commercant'])

    nom_boutique = serializers.CharField(required=False, allow_blank=True)
    adresse = serializers.CharField(required=False, allow_blank=True)
    photo_identite = serializers.ImageField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email existe déjà.")
        return value

    def validate_telephone(self, value):
        if Utilisateurs.objects.filter(telephone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone existe déjà.")
        return value

    def validate(self, data):
        if data.get('role') == 'commercant' and not data.get('nom_boutique'):
            raise serializers.ValidationError(
                "Le nom de la boutique est obligatoire pour un commerçant."
            )
        return data


class ConnexionSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Identifiants incorrects.")
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        try:
            utilisateur = user.utilisateur
            if utilisateur.statut_compte == 'bloque':
                raise serializers.ValidationError("Ce compte est bloqué.")
            if utilisateur.statut_compte == 'suspendu':
                raise serializers.ValidationError("Ce compte est suspendu.")
        except Utilisateurs.DoesNotExist:
            raise serializers.ValidationError("Profil utilisateur introuvable.")
        data['user'] = user
        return data


class OTPSerializer(serializers.Serializer):
    """Serializer pour vérifier le code OTP (2FA)"""
    username = serializers.CharField()
    code_otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
            utilisateur = user.utilisateur
            otp = Authentification.objects.filter(
                id_utilisateur=utilisateur,
                code_otp=data['code_otp'],
                utilise=False,
                expiration__gt=timezone.now()
            ).last()
            if not otp:
                raise serializers.ValidationError("Code OTP invalide ou expiré.")
            data['otp_obj'] = otp
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")
        return data


class DeconnexionSerializer(serializers.Serializer):
    """Serializer pour la déconnexion (révocation du token)"""
    refresh_token = serializers.CharField()


class ChangerMotDePasseSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    ancien_mot_de_passe = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, min_length=8)
    confirmer_mot_de_passe = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['nouveau_mot_de_passe'] != data['confirmer_mot_de_passe']:
            raise serializers.ValidationError(
                "Les deux mots de passe ne correspondent pas."
            )
        return data


class AttribuerRoleAdminSerializer(serializers.Serializer):
    """Serializer pour attribuer un rôle d'administrateur"""
    id_utilisateur = serializers.IntegerField()
    
    def validate(self, data):
        try:
            utilisateur = Utilisateurs.objects.get(id_utilisateur=data['id_utilisateur'])
            if utilisateur.role == 'admin':
                raise serializers.ValidationError("Cet utilisateur est déjà administrateur.")
            data['utilisateur'] = utilisateur
        except Utilisateurs.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")
        return data


class ListeUtilisateursSerializer(serializers.ModelSerializer):
    """Serializer pour afficher la liste des utilisateurs"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Utilisateurs
        fields = ['id_utilisateur', 'username', 'email', 'telephone', 'role', 'statut_compte', 'date_creation']
        read_only_fields = fields


class ModifierPermissionsAdminSerializer(serializers.Serializer):
    """Serializer pour modifier les permissions d'un administrateur"""
    id_utilisateur = serializers.IntegerField()
    peut_valider_depot = serializers.BooleanField(required=False)
    peut_valider_retrait = serializers.BooleanField(required=False)
    peut_bloquer_utilisateur = serializers.BooleanField(required=False)
    
    def validate(self, data):
        try:
            utilisateur = Utilisateurs.objects.get(id_utilisateur=data['id_utilisateur'])
            if utilisateur.role != 'admin':
                raise serializers.ValidationError("Cet utilisateur n'est pas administrateur.")
            data['utilisateur'] = utilisateur
        except Utilisateurs.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")
        return data