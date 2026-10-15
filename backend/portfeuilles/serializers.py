from rest_framework import serializers
from portfeuilles.models import Portefeuilles
from compte.models import Utilisateurs


class PortefeuilleSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un portefeuille"""
    proprietaire = serializers.SerializerMethodField()
    telephone = serializers.SerializerMethodField()

    class Meta:
        model = Portefeuilles
        fields = [
            'id_portefeuille',
            'proprietaire',
            'telephone',
            'solde',
            'date_creation',
        ]

    def get_proprietaire(self, obj):
        return obj.id_utilisateur.user.username

    def get_telephone(self, obj):
        return obj.id_utilisateur.telephone


class SoldeSerializer(serializers.Serializer):
    """Serializer pour afficher uniquement le solde"""
    solde = serializers.DecimalField(max_digits=10, decimal_places=2)
    proprietaire = serializers.CharField()


class TransfertSerializer(serializers.Serializer):
    """Serializer pour un transfert entre portefeuilles"""
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
    
    def validate(self, data):
        user = self.context['request'].user
        if user.utilisateur.telephone == data['telephone_destinataire']:
            raise serializers.ValidationError("Vous ne pouvez pas transférer à vous-même.")
        return data


class DepotSerializer(serializers.Serializer):
    """Serializer pour une demande de dépôt"""
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value


class RetraitSerializer(serializers.Serializer):
    """Serializer pour une demande de retrait"""
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value