from django.db import models
from compte.models import Utilisateurs


class QRCode(models.Model):
    id_qr = models.AutoField(primary_key=True)
    id_commercant = models.OneToOneField(
        Utilisateurs,
        on_delete=models.CASCADE,
        related_name='qr_code_commercant',
        limit_choices_to={'role': 'commercant'},
    )
    code_qr = models.CharField(max_length=255, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qr_codes'

    def __str__(self):
        return f"QR {self.id_commercant.user.username}"


class PaiementsCommercants(models.Model):
    id_paiement = models.AutoField(primary_key=True)
    id_client = models.ForeignKey(
        Utilisateurs,
        on_delete=models.CASCADE,
        related_name='paiements_effectues',
        limit_choices_to={'role': 'client'},
    )
    id_commercant = models.ForeignKey(
        Utilisateurs,
        on_delete=models.CASCADE,
        related_name='paiements_recus',
        limit_choices_to={'role': 'commercant'},
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    date_paiement = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paiements_commercants'

    def __str__(self):
        return f"Paiement {self.reference} ({self.montant})"
