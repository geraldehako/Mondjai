# Generated by Django 4.1.7 on 2024-08-10 11:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="utilisateurs",
            name="profession",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="utilisateurs",
            name="telephone",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="utilisateurs",
            name="statut",
            field=models.CharField(
                choices=[("ACTIF", "Actif"), ("NONACTIF", "Non Actif")],
                max_length=10,
                null=True,
                verbose_name="Statut",
            ),
        ),
    ]
