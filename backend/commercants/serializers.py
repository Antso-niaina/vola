from rest_framework import serializers
from commercants.models import PaiementsCommercants, QRCode
from compte.models import Utilisateurs


class QRCodeSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un QR code"""
    commercant = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            'id_qr',
            'commercant',
            'code_qr',
            'date_creation',
        ]

    def get_commercant(self, obj):
        return obj.id_commercant.user.username


class PaiementCommercantSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un paiement"""
    client = serializers.SerializerMethodField()
    commercant = serializers.SerializerMethodField()

    class Meta:
        model = PaiementsCommercants
        fields = [
            'id_paiement',
            'client',
            'commercant',
            'montant',
            'reference',
            'date_paiement',
        ]

    def get_client(self, obj):
        return obj.id_client.user.username

    def get_commercant(self, obj):
        return obj.id_commercant.user.username


class PaiementQRSerializer(serializers.Serializer):
    """Serializer pour effectuer un paiement via QR code"""
    code_qr = serializers.CharField()
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value

    def validate_code_qr(self, value):
        if not QRCode.objects.filter(code_qr=value).exists():
            raise serializers.ValidationError("QR code invalide ou inexistant.")
        return value


class GenerationQRSerializer(serializers.Serializer):
    """Serializer pour générer un QR code commerçant"""
    id_commercant = serializers.IntegerField()

    def validate_id_commercant(self, value):
        if not Utilisateurs.objects.filter(
            id_utilisateur=value,
            role='commercant'
        ).exists():
            raise serializers.ValidationError("Commerçant introuvable.")
        return value