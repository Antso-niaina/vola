

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compte', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaiementsCommercants',
            fields=[
                ('id_paiement', models.AutoField(primary_key=True, serialize=False)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('date_paiement', models.DateTimeField(auto_now_add=True)),
                ('id_client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='paiements_effectues', to='compte.utilisateurs')),
                ('id_commercant', models.ForeignKey(limit_choices_to={'role': 'commercant'}, on_delete=django.db.models.deletion.CASCADE, related_name='paiements_recus', to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'paiements_commercants',
            },
        ),
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id_qr', models.AutoField(primary_key=True, serialize=False)),
                ('code_qr', models.CharField(max_length=255, unique=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('id_commercant', models.OneToOneField(limit_choices_to={'role': 'commercant'}, on_delete=django.db.models.deletion.CASCADE, related_name='qr_code_commercant', to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'qr_codes',
            },
        ),
    ]
