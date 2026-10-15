

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilisateurs',
            fields=[
                ('id_utilisateur', models.AutoField(primary_key=True, serialize=False)),
                ('telephone', models.CharField(max_length=20, unique=True)),
                ('photo_identite', models.ImageField(blank=True, null=True, upload_to='photos_identite/')),
                ('role', models.CharField(choices=[('client', 'Client'), ('commercant', 'Commerçant'), ('admin', 'Administrateur')], default='client', max_length=20)),
                ('statut_compte', models.CharField(choices=[('actif', 'Actif'), ('suspendu', 'Suspendu'), ('bloque', 'Bloqué')], default='actif', max_length=20)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='utilisateur', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('utilisateurs_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='compte.utilisateurs')),
                ('peut_valider_depot', models.BooleanField(default=True)),
                ('peut_valider_retrait', models.BooleanField(default=True)),
                ('peut_bloquer_utilisateur', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'admins',
            },
            bases=('compte.utilisateurs',),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('utilisateurs_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='compte.utilisateurs')),
                ('nombre_transactions', models.IntegerField(default=0)),
                ('nombre_tentatives_echouees', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'clients',
            },
            bases=('compte.utilisateurs',),
        ),
        migrations.CreateModel(
            name='Commercant',
            fields=[
                ('utilisateurs_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='compte.utilisateurs')),
                ('nom_boutique', models.CharField(max_length=200)),
                ('adresse', models.TextField(blank=True, null=True)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
            ],
            options={
                'db_table': 'commercants',
            },
            bases=('compte.utilisateurs',),
        ),
        migrations.CreateModel(
            name='Authentification',
            fields=[
                ('id_auth', models.AutoField(primary_key=True, serialize=False)),
                ('code_otp', models.CharField(max_length=6, null=True)),
                ('expiration', models.DateTimeField(null=True)),
                ('utilise', models.BooleanField(default=False)),
                ('id_utilisateur', models.ForeignKey(db_column='id_utilisateur', on_delete=django.db.models.deletion.CASCADE, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'authentifications',
            },
        ),
        migrations.CreateModel(
            name='Journaux',
            fields=[
                ('id_log', models.AutoField(primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=255)),
                ('date_action', models.DateTimeField(auto_now_add=True)),
                ('id_utilisateur', models.ForeignKey(db_column='id_utilisateur', null=True, on_delete=django.db.models.deletion.SET_NULL, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'journaux',
            },
        ),
    ]
