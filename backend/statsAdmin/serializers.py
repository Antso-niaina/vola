from rest_framework import serializers

class NbrUtilisateursSerializer(serializers.Serializer):
    total_utilisateurs = serializers.IntegerField()
class NbrtransactionsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
class ListeDepotsAttenteSerializer(serializers.Serializer):
    id_depot = serializers.IntegerField()
    nom_utilisateur = serializers.CharField()
    telephone = serializers.CharField() 
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()   
    date_demande = serializers.DateTimeField() 

class ListeRetraitsAttenteSerializer(serializers.Serializer):
    id_retrait = serializers.IntegerField()
    nom_utilisateur = serializers.CharField()
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)
    date_retrait = serializers.DateTimeField()

class TopCommercantsSerializer(serializers.Serializer):
    nom_commercant = serializers.CharField()
    nom_boutique = serializers.CharField()
    total_recu = serializers.DecimalField(max_digits=15, decimal_places=2)
    nombre_paiements = serializers.IntegerField()
 
class TopUtilisateursSerializer(serializers.Serializer):
    nom_utilisateur = serializers.CharField()
    telephone = serializers.CharField()    
    total_envoye = serializers.DecimalField(max_digits=15, decimal_places=2)
    nombre_transactions = serializers.IntegerField()

class TransactionsParPeriodeSerializer(serializers.Serializer):
    periode = serializers.CharField()
    nombre_transactions = serializers.IntegerField()
    volume_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    type_periode = serializers.CharField()   