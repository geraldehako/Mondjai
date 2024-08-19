from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser


class Utilisateurs(AbstractUser):
    
    GESTIONNAIRE = 'GESTIONNAIRE'
    CLIENT = 'CLIENT'
    ADMINISTRATEUR = 'ADMINISTRATEUR'
    ADMINISTRATEURSUPER = 'ADMINISTRATEURSUPER'

    MASCULIN = 'MASCULIN'
    FEMININ = 'FEMININ'

    MARIE = 'MARIE(E)'
    CELIBATAIRE = 'CELIBATAIRE'

    ACTIF = 'ACTIF'
    NONACTIF = 'NONACTIF'

    ROLE_CHOICES = (
        (GESTIONNAIRE, 'Gestionnaire'),
        (CLIENT,'Client'),
        (ADMINISTRATEUR, 'Administrateur'),
        (ADMINISTRATEURSUPER, 'Administrateur Super'),
    )

    GENRE_CHOICES = (
        (MASCULIN, 'Masculin'),
        (FEMININ,'Feminin'),
    )

    MATRIMONIALE_CHOICES = (
        (MARIE, 'Marié(e)'),
        (CELIBATAIRE,'Célibataire'),
    )

    STATUT_CHOICES = (
        (ACTIF, 'Actif'),
        (NONACTIF,'Non Actif'),
    )

    photo = models.ImageField(verbose_name='photo de profil', upload_to='Mediatheques/', null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='rôle')
    statut = models.CharField(max_length=10,choices=STATUT_CHOICES, verbose_name='Statut', null=True)
    sexe = models.CharField(max_length=10, choices=GENRE_CHOICES, verbose_name='Genre')
    matrimoniale = models.CharField(max_length=50,choices=MATRIMONIALE_CHOICES, verbose_name='Situation Matrimoniale')
    nombre_enfant = models.PositiveIntegerField(default=12)
    profession = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20, null=True)
    date_inscription = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_role_display()}"