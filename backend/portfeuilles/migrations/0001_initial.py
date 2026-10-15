

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compte', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portefeuilles',
            fields=[
                ('id_portefeuille', models.AutoField(primary_key=True, serialize=False)),
                ('solde', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('id_utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compte.utilisateurs')),
            ],
            options={
                'db_table': 'portefeuilles',
            },
        ),
    ]
