from django.db import models
from compte.models import Utilisateurs

class Portefeuilles(models.Model):
    id_portefeuille = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portefeuilles'
    
    def __str__(self):
        return f"Portefeuille de {self.id_utilisateur.user.username} - Solde: {self.solde}"