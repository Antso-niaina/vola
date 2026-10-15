

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compte', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Depots',
            fields=[
                ('id_depot', models.AutoField(primary_key=True, serialize=False)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('en_attente', 'En attente'), ('validee', 'Validée'), ('refusee', 'Refusée')], default='en_attente', max_length=20)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('id_admin', models.ForeignKey(blank=True, db_column='id_admin', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depots_admin', to='compte.utilisateurs')),
                ('id_utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'depots',
            },
        ),
        migrations.CreateModel(
            name='Retrait',
            fields=[
                ('id_retrait', models.AutoField(primary_key=True, serialize=False)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('en_attente', 'En attente'), ('validee', 'Validée'), ('refusee', 'Refusée')], default='en_attente', max_length=20)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('id_admin', models.ForeignKey(blank=True, db_column='id_admin', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retraits_admin', to='compte.utilisateurs')),
                ('id_utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'retraits',
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id_transaction', models.AutoField(primary_key=True, serialize=False)),
                ('type_transaction', models.CharField(choices=[('envoi', 'Envoi'), ('reception', 'Réception'), ('depot', 'Dépôt'), ('retrait', 'Retrait'), ('transfert', 'Transfert'), ('paiement', 'Paiement')], max_length=50)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('en_attente', 'En attente'), ('validee', 'Validée'), ('echec', 'Échec'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('date_transaction', models.DateTimeField(auto_now_add=True)),
                ('id_destinataire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_destinataire', to='compte.utilisateurs')),
                ('id_expediteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_expediteur', to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'transactions',
            },
        ),
    ]
