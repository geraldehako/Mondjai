# Generated by Django 4.1.7 on 2024-08-16 14:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "Gestions",
            "0002_categoriee_categories_configabonnement_presentation_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="presentation",
            name="site",
            field=models.CharField(max_length=50, null=True),
        ),
    ]
