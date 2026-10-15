from rest_framework import serializers
from django.contrib.auth.models import User
from compte.models import Utilisateurs, Client, Commercant, Admin


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour le User Django"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer de base pour tous les utilisateurs"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Utilisateurs
        fields = [
            'id_utilisateur',
            'user',
            'telephone',
            'photo_identite',
            'role',
            'statut_compte',
            'date_creation',
        ]


class ClientSerializer(serializers.ModelSerializer):
    """Serializer spécifique au client"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id_utilisateur',
            'user',
            'telephone',
            'photo_identite',
            'role',
            'statut_compte',
            'date_creation',
            'nombre_transactions',
            'nombre_tentatives_echouees',
        ]


class CommercantSerializer(serializers.ModelSerializer):
    """Serializer spécifique au commerçant"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Commercant
        fields = [
            'id_utilisateur',
            'user',
            'telephone',
            'photo_identite',
            'role',
            'statut_compte',
            'date_creation',
            'nom_boutique',
            'adresse',
            'qr_code',
        ]


class AdminSerializer(serializers.ModelSerializer):
    """Serializer spécifique à l'admin"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Admin
        fields = [
            'id_utilisateur',
            'user',
            'telephone',
            'photo_identite',
            'role',
            'statut_compte',
            'date_creation',
            'peut_valider_depot',
            'peut_valider_retrait',
            'peut_bloquer_utilisateur',
        ]


class UtilisateurUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour modifier le profil"""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = Utilisateurs
        fields = [
            'telephone',
            'photo_identite',
            'first_name',
            'last_name',
            'email',
        ]

    def update(self, instance, validated_data):
        
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BlockUserSerializer(serializers.Serializer):
    """Serializer pour bloquer/débloquer un utilisateur (admin)"""
    id_utilisateur = serializers.IntegerField()
    statut = serializers.ChoiceField(choices=['actif', 'suspendu', 'bloque'])

    def validate_id_utilisateur(self, value):
        if not Utilisateurs.objects.filter(id_utilisateur=value).exists():
            raise serializers.ValidationError("Utilisateur introuvable.")
        return value

class AttribuerRoleAdminSerializer(serializers.Serializer):
    """Serializer pour attribuer le rôle admin à un utilisateur"""
    id_utilisateur = serializers.IntegerField()
    peut_valider_depot = serializers.BooleanField(default=True)
    peut_valider_retrait = serializers.BooleanField(default=True)
    peut_bloquer_utilisateur = serializers.BooleanField(default=True)

    def validate_id_utilisateur(self, value):
        if not Utilisateurs.objects.filter(id_utilisateur=value).exists():
            raise serializers.ValidationError("Utilisateur introuvable.")
        utilisateur = Utilisateurs.objects.get(id_utilisateur=value)
        if utilisateur.role == 'admin':
            raise serializers.ValidationError("Cet utilisateur est déjà admin.")
        return value


class ModifierPermissionsAdminSerializer(serializers.Serializer):
    """Serializer pour modifier les permissions d'un admin"""
    peut_valider_depot = serializers.BooleanField(required=False)
    peut_valider_retrait = serializers.BooleanField(required=False)
    peut_bloquer_utilisateur = serializers.BooleanField(required=False)
