# models.py
from datetime import timezone
from django.contrib.auth.models import User
from django.db import models
from Accounts.models import Utilisateurs

class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Categoriee(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Categories(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
class Entree(models.Model):
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, null=True)
    categorie = models.ForeignKey(Categoriee, on_delete=models.CASCADE,null=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

class Depense(models.Model):
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

class Investir(models.Model):
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, null=True)
    categorie = models.ForeignKey(Categories, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

class Abonnement(models.Model):
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_actif = models.BooleanField(default=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    nature = models.CharField(max_length=50, null=True)

class Configabonnement(models.Model):
    montant = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    pourcentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    date = models.DateField(auto_now_add=True, null=True)

class Transactionabonnement(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateurs,
        on_delete=models.CASCADE,
        related_name='transactions_abonnement',
        null=True,
        blank=True
    )

    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut = models.DateField()
    date_fin = models.DateField()


class Presentation(models.Model):
    logo = models.ImageField(upload_to='Mediatheques/', null=True, blank=True)
    contact = models.CharField(max_length=15)
    presentation_text = models.TextField()
    welcome_message = models.TextField()
    video_url = models.URLField(max_length=200)
    site = models.CharField(max_length=50, null=True)
    pub = models.ImageField(upload_to='Mediatheques/', null=True, blank=True)
    email = models.CharField(max_length=50)
    whatsapp = models.URLField(max_length=200, null=True, blank=True) 
    facebook = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "Presentation Data"



