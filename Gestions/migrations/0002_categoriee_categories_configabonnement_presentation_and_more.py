# Generated by Django 4.1.7 on 2024-08-16 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Gestions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Categoriee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Categories",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Configabonnement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "montant",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "pourcentage",
                    models.DecimalField(decimal_places=2, max_digits=5, null=True),
                ),
                ("date", models.DateField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Presentation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, upload_to="Mediatheques/"),
                ),
                ("contact", models.CharField(max_length=15)),
                ("presentation_text", models.TextField()),
                ("welcome_message", models.TextField()),
                ("video_url", models.URLField()),
                (
                    "pub",
                    models.ImageField(blank=True, null=True, upload_to="Mediatheques/"),
                ),
                ("email", models.CharField(max_length=50)),
                ("whatsapp", models.URLField(blank=True, null=True)),
                ("facebook", models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="entree",
            name="libelle",
        ),
        migrations.AddField(
            model_name="abonnement",
            name="montant",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
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
        migrations.CreateModel(
            name="Transactionabonnement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("montant", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date_debut", models.DateField()),
                ("date_fin", models.DateField()),
                (
                    "utilisateur",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions_abonnement",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Investir",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(auto_now_add=True, null=True)),
                ("montant", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "categorie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Gestions.categories",
                    ),
                ),
                (
                    "utilisateur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="entree",
            name="categorie",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Gestions.categoriee",
            ),
        ),
    ]
