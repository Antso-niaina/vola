from django.db import models
from compte.models import Utilisateurs


class TokenBlacklist(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.TextField()
    date_expiration = models.DateTimeField()
    date_revocation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tokens_blacklist'

    def __str__(self):
        return f"Token révoqué le {self.date_revocation}"


class TentativeConnexion(models.Model):
    TYPE_TENTATIVE_CHOICES = [
        ('login', 'Login'),
        ('otp', 'OTP'),
    ]

    id = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(
        Utilisateurs,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    type_tentative = models.CharField(
        max_length=10,
        choices=TYPE_TENTATIVE_CHOICES,
        default='login'
    )
    telephone = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    succes = models.BooleanField(default=False)
    date_tentative = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tentatives_connexion'

    def __str__(self):
        statut = "réussie" if self.succes else "échouée"
        return f"Tentative {self.type_tentative} {statut} - {self.telephone} - {self.date_tentative}"