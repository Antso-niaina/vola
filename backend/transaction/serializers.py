from rest_framework import serializers
from transaction.models import Transactions, Depots, Retrait
from compte.models import Utilisateurs


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer pour afficher une transaction"""
    expediteur = serializers.SerializerMethodField()
    destinataire = serializers.SerializerMethodField()
    expediteur_telephone = serializers.SerializerMethodField()
    destinataire_telephone = serializers.SerializerMethodField()

    class Meta:
        model = Transactions
        fields = [
            'id_transaction',
            'type_transaction',
            'montant',
            'expediteur',
            'expediteur_telephone',
            'destinataire',
            'destinataire_telephone',
            'reference',
            'status',
            'date_transaction',
        ]

    def get_expediteur(self, obj):
        return obj.id_expediteur.user.username

    def get_expediteur_telephone(self, obj):
        return obj.id_expediteur.telephone

    def get_destinataire(self, obj):
        return obj.id_destinataire.user.username

    def get_destinataire_telephone(self, obj):
        return obj.id_destinataire.telephone


class EnvoiArgentSerializer(serializers.Serializer):
    """Serializer pour envoyer de l'argent"""
    telephone_destinataire = serializers.CharField(max_length=20)
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value

    def validate_telephone_destinataire(self, value):
        if not Utilisateurs.objects.filter(telephone=value).exists():
            raise serializers.ValidationError("Aucun utilisateur trouvé avec ce numéro.")
        return value


class DepotSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un dépôt"""
    utilisateur = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Depots
        fields = [
            'id_depot',
            'utilisateur',
            'montant',
            'admin',
            'status',
            'date_demande',
            'date_validation',
        ]

    def get_utilisateur(self, obj):
        return obj.id_utilisateur.user.username

    def get_admin(self, obj):
        if obj.id_admin:
            return obj.id_admin.user.username
        return None


class DemandeDepotSerializer(serializers.Serializer):
    """Serializer pour faire une demande de dépôt"""
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value


class ValiderDepotSerializer(serializers.Serializer):
    """Serializer pour valider ou refuser un dépôt (admin)"""
    id_depot = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=['validee', 'refusee'])

    def validate_id_depot(self, value):
        if not Depots.objects.filter(id_depot=value).exists():
            raise serializers.ValidationError("Dépôt introuvable.")
        depot = Depots.objects.get(id_depot=value)
        if depot.status != 'en_attente':
            raise serializers.ValidationError("Ce dépôt a déjà été traité.")
        return value


class RetraitSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un retrait"""
    utilisateur = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Retrait
        fields = [
            'id_retrait',
            'utilisateur',
            'montant',
            'admin',
            'status',
            'date_demande',
            'date_validation',
        ]

    def get_utilisateur(self, obj):
        return obj.id_utilisateur.user.username

    def get_admin(self, obj):
        if obj.id_admin:
            return obj.id_admin.user.username
        return None


class DemandeRetraitSerializer(serializers.Serializer):
    """Serializer pour faire une demande de retrait"""
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value


class ValiderRetraitSerializer(serializers.Serializer):
    """Serializer pour valider ou refuser un retrait (admin)"""
    id_retrait = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=['validee', 'refusee'])

    def validate_id_retrait(self, value):
        if not Retrait.objects.filter(id_retrait=value).exists():
            raise serializers.ValidationError("Retrait introuvable.")
        retrait = Retrait.objects.get(id_retrait=value)
        if retrait.status != 'en_attente':
            raise serializers.ValidationError("Ce retrait a déjà été traité.")
        return value
