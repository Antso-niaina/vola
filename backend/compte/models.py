from django.db import models
from django.contrib.auth.models import User

class Utilisateurs(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('commercant', 'Commerçant'),
        ('admin', 'Administrateur'),
    ]
    id_utilisateur = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='utilisateur',
        db_column='user_id'
    )
    telephone = models.CharField(max_length=20, unique=True)
    photo_identite = models.ImageField(
        upload_to='photos_identite/', null=True, blank=True
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='client'
    )
    statut_compte = models.CharField(
        max_length=20,
        choices=[
            ('actif', 'Actif'),
            ('suspendu', 'Suspendu'),
            ('bloque', 'Bloqué'),
        ],
        default='actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilisateurs'

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Client(Utilisateurs):
    nombre_transactions = models.IntegerField(default=0)
    nombre_tentatives_echouees = models.IntegerField(default=0)

    class Meta:
        db_table = 'clients'

    def __str__(self):
        return f"Client: {self.user.username}"


class Commercant(Utilisateurs):
    nom_boutique = models.CharField(max_length=200)
    adresse = models.TextField(null=True, blank=True)
    qr_code = models.ImageField(
        upload_to='qr_codes/', null=True, blank=True
    )

    class Meta:
        db_table = 'commercants'

    def __str__(self):
        return f"Commerçant: {self.nom_boutique}"


class Admin(Utilisateurs):
    peut_valider_depot = models.BooleanField(default=True)
    peut_valider_retrait = models.BooleanField(default=True)
    peut_bloquer_utilisateur = models.BooleanField(default=True)

    class Meta:
        db_table = 'admins'

    def __str__(self):
        return f"Admin: {self.user.username}"


class Authentification(models.Model):
    id_auth = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(
        Utilisateurs, db_column='id_utilisateur', on_delete=models.CASCADE
    )
    code_otp = models.CharField(max_length=6, null=True)
    expiration = models.DateTimeField(null=True)
    utilise = models.BooleanField(default=False)

    class Meta:
        db_table = 'authentifications'


class Journaux(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(
        Utilisateurs, db_column='id_utilisateur',
        on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journaux'

    def __str__(self):
        return f"{self.id_utilisateur} - {self.action}"