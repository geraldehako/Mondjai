# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Categorie, Categoriee,Categories, Entree, Depense,Investir, Abonnement,Presentation
from Accounts.models import Utilisateurs
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
#class UserSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = User
#        fields = ['id', 'username', 'email']
 
class CategorieSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'

class CategorieeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoriee
        fields = '__all__'

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
# class EntreeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Entree
#         fields = ['id', 'utilisateur', 'date', 'libelle', 'montant']
#         read_only_fields = ['utilisateur']

class EntreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entree
        fields = ['id', 'utilisateur', 'date', 'categorie', 'montant']
        read_only_fields = ['utilisateur']

class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'utilisateur', 'date', 'categorie', 'montant']
        read_only_fields = ['utilisateur']

class InvestirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investir
        fields = ['id', 'utilisateur', 'date', 'categorie', 'montant']
        read_only_fields = ['utilisateur']

class AbonnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abonnement
        fields = ['id', 'utilisateur', 'date_debut', 'date_fin', 'est_actif','montant','nature']
        read_only_fields = ['utilisateur']


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateurs
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'sexe', 'matrimoniale', 'nombre_enfant', 'photo']


class PresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presentation
        fields = ['logo', 'contact', 'presentation_text', 'welcome_message', 'video_url','site','pub','email','whatsapp','facebook']


