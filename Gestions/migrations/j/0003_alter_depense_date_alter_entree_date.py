# Generated by Django 4.1.7 on 2024-08-05 19:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Gestions", "0002_categoriee_remove_entree_libelle_entree_categorie"),
    ]

    operations = [
        migrations.AlterField(
            model_name="depense",
            name="date",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="entree",
            name="date",
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
