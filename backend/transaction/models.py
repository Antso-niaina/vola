from django.db import models
from compte.models import Utilisateurs

class Transactions(models.Model):
    TYPE_CHOICES = [
        ('envoi', 'Envoi'),
        ('reception', 'Réception'),
        ('depot', 'Dépôt'),
        ('retrait', 'Retrait'),
        ('transfert', 'Transfert'),
        ('paiement', 'Paiement'),
    ]
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('echec', 'Échec'),
        ('annulee', 'Annulée'),
    ]
    id_transaction = models.AutoField(primary_key=True)
    type_transaction = models.CharField(max_length=50,choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    id_expediteur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='transactions_expediteur')
    id_destinataire = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='transactions_destinataire')
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_transaction = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
    
    def __str__(self):
        return f"Transaction {self.id_transaction} - {self.type_transaction} - Montant: {self.montant}"

class Depots(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]
    id_depot = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    id_admin = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='depots_admin', db_column='id_admin', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'depots'
    
    def __str__(self):
        return f"Depot {self.id_depot} - Utilisateur: {self.id_utilisateur.user.username} - Montant: {self.montant}"

class Retrait(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]
    id_retrait = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    id_admin = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='retraits_admin', db_column='id_admin', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'retraits'
    
    def __str__(self):
        return f"Retrait {self.id_retrait} - Utilisateur: {self.id_utilisateur.user.username} - Montant: {self.montant}"