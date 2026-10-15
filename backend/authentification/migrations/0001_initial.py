

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compte', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenBlacklist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token', models.TextField()),
                ('date_expiration', models.DateTimeField()),
                ('date_revocation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tokens_blacklist',
            },
        ),
        migrations.CreateModel(
            name='TentativeConnexion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type_tentative', models.CharField(choices=[('login', 'Login'), ('otp', 'OTP')], default='login', max_length=10)),
                ('telephone', models.CharField(max_length=20)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('succes', models.BooleanField(default=False)),
                ('date_tentative', models.DateTimeField(auto_now_add=True)),
                ('id_utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'tentatives_connexion',
            },
        ),
    ]
