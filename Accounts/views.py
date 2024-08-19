# back office
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
# Importations spécifiques au projet
from .forms import UsernameChangeForm, CustomPasswordChangeForm,UtilisateurForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from .forms import UtilisateurForm,UtilisateurmForm
from .models import Utilisateurs
from django.db import models
from Gestions.models import Configabonnement
# AUTHENTIFICATION--------------------------------------------------------------------------------------------
# Create your views here.

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if request.user.role == 'GESTIONNAIRE':
                return redirect('menu')
            elif request.user.role == 'ADMINISTRATEURSUPER':
                return redirect('menu')

    return render(request,'Pages/Log/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

# CLIENTS_____________________________________________________________________________________________________________________________________________
# Vue pour la liste des genres
@login_required(login_url='/')
def liste_client(request):
    clients = Utilisateurs.objects.filter(role='CLIENT')
    return render(request, 'Pages/Clients/liste_clients.html', {'clients': clients})

# UTILISATEURS_____________________________________________________________________________________________________________________________________________
def liste_utilisateur(request):
    clients = Utilisateurs.objects.filter(role='GESTIONNAIRE')
    return render(request, 'Pages/Utilisateurs/liste_utilisateurs.html', {'clients': clients})

# Vue pour creer un utlisateur
def create_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            # Affichage des informations soumises
            print("Nom :", form.cleaned_data.get('first_name'))
            print("Prénoms :", form.cleaned_data.get('last_name'))
            print("Identifiant :", form.cleaned_data.get('username'))
            print("Email :", form.cleaned_data.get('email'))
            print("Sexe :", form.cleaned_data.get('sexe'))
            print("Situation Matrimoniale :", form.cleaned_data.get('matrimoniale'))
            print("Nombre d'enfants :", form.cleaned_data.get('nombre_enfant'))
            print("Profession :", form.cleaned_data.get('profession'))
            print("Téléphone :", form.cleaned_data.get('telephone'))
            print("Photo :", request.FILES.get('photo'))
            # Ici vous pouvez ajouter d'autres champs si nécessaire

            # Configuration des valeurs par défaut pour statut et rôle
            form.instance.statut = 'Actif'
            form.instance.role = 'GESTIONNAIRE'

            # Gestion du mot de passe
            password = 'P@ssword'
            encoded_password = make_password(password)
            form.instance.password = encoded_password

            # Enregistrement du formulaire
            form.save()

            # Redirection après création
            return redirect('liste_gestionnaires')
        else:
            # Si le formulaire n'est pas valide, imprime les erreurs
            print("Formulaire invalide :", form.errors)
    else:
        form = UtilisateurForm()
    
    return render(request, 'Pages/Utilisateurs/create_utilisateur.html', {'form': form})



# Vue pour modifier un client
def modifier_utilisateur(request, client_id):
    utilisateur = get_object_or_404(Utilisateurs, pk=client_id)
    if request.method == 'POST':
        client_form = UtilisateurmForm(request.POST, request.FILES, instance=utilisateur)
        if client_form.is_valid():
            client_form.save()
            return redirect('liste_gestionnaires')
    else:
        client_form = UtilisateurmForm(instance=utilisateur)
    return render(request, 'Pages/Utilisateurs/update_utilisateur.html', {'form': client_form, 'utilisateur': utilisateur})

# Vue pour supprimer un client
def supprimer_utilisateur(request, client_id):
    utilisateur = get_object_or_404(Utilisateurs, pk=client_id)
    if request.method == 'POST':
        utilisateur.delete()
        return redirect('liste_gestionnaires')
    return render(request, 'Pages/Utilisateurs/delete_utilisateur.html', {'utilisateur': utilisateur})

# Vue pour supprimer un client
def supprimer_client(request, client_id):
    utilisateur = get_object_or_404(Utilisateurs, pk=client_id)
    if request.method == 'POST':
        utilisateur.delete()
        return redirect('liste_clients')
    return render(request, 'Pages/Clients/delete_client.html', {'utilisateur': utilisateur})

#update mot de passe et login client 
@login_required
def change_usernamecl(request, idact):
    """
    Fonction pour changer le nom d'utilisateur de l'utilisateur connecté.
    """
    action = get_object_or_404(Utilisateurs, pk=idact)
    Util = get_object_or_404(Utilisateurs, pk=idact)
    
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, instance=Util)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre nom d\'utilisateur a été mis à jour avec succès.')
            return redirect('liste_clients')
    else:
        form = UsernameChangeForm(instance=Util)
    
    return render(request, 'Pages/Utilisateurs/change_username.html', {'form': form})

@login_required
def change_passwordcl(request, idact):
    """
    Fonction pour changer le mot de passe de l'utilisateur connecté.
    """
    action = get_object_or_404(Utilisateurs, pk=idact)
    Util = get_object_or_404(Utilisateurs, pk=idact)
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(Util, request.POST)
        if form.is_valid():
            #user = form.save()
            form.save()
            #update_session_auth_hash(request, user)  # Important pour maintenir l'utilisateur connecté après le changement de mot de passe
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('liste_clients')
    else:
        form = CustomPasswordChangeForm(Util)
    
    return render(request, 'Pages/Utilisateurs/change_password.html', {'form': form})
#___________________________________________________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________________________________________

#___________________________________________________________________________________________________________________________________________________________

#___________________________________________________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________________________________________

# views.py

from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken

from Gestions.models import Abonnement
from .forms import UtilisateursCreationForm, UtilisateursChangeForm
from .models import Utilisateurs
from Gestions.serializers import UtilisateurSerializer


# Vue pour deconnection
@csrf_exempt
def logout_userbank(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# Vue pour l'inscription des utilisateurs via formulaire
def register1(request):
    if request.method == 'POST':
        form = UtilisateursCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil après l'inscription
    else:
        form = UtilisateursCreationForm()
    return render(request, 'register.html', {'form': form})

# Vue pour la modification du profil utilisateur
def edit_profile(request):
    if request.method == 'POST':
        form = UtilisateursChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirige vers la page de profil après modification
    else:
        form = UtilisateursChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

# Vue pour obtenir le jeton CSRF
@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

# Vue pour l'inscription des utilisateurs via API
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Permettre l'accès sans authentification pour l'inscription
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    sexe = request.data.get('sexe')
    tel = request.data.get('tel')
    prof = request.data.get('prof')
    enf = request.data.get('enf')

    if not username or not password or not email:
        return Response({'error': 'Username, password and email are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = Utilisateurs.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name,role='CLIENT',sexe=sexe,statut='actif',telephone=tel,profession=prof,nombre_enfant=enf)
    
    # Date actuelle
    today = timezone.now().date()
    
    # Date de fin 30 jours après la date actuelle
    date_fin = today + timedelta(days=30)

    abons = Configabonnement.objects.filter().first()
    
    # Création de l'abonnement
    abonnement = Abonnement.objects.create(
        utilisateur=user,
        date_debut=today,
        date_fin=date_fin,
        montant=(abons.montant -((abons.montant * abons.pourcentage)/100)),
        est_actif=True,
        nature='ESSAI'
        #nature='PREMIUM'
    )
    
    # Création du token
    token, created = Token.objects.get_or_create(user=user)
    #return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    # Retourne une réponse avec les informations de l'utilisateur et du token
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'token': token.key
    }, status=status.HTTP_201_CREATED)

# Vue personnalisée pour l'authentification avec token
class CustomAuthToken1(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'role': getattr(user, 'role', None),  # Assurez-vous que le champ 'role' existe dans votre modèle utilisateur
            'last_login': user.last_login,
            'email': user.email,
            'user_id': user.pk,
            'username': user.username,
            # 'photo': user.photo,  # Décommentez si le champ 'photo' existe dans votre modèle utilisateur
        })
    
class CustomAuthToken2(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Vérifier la date de fin de l'abonnement
        today = timezone.now().date()
        try:
            abonnement = Abonnement.objects.get(utilisateur=user)
            if abonnement.date_fin < today:
                return Response({'error': 'Abonnement expiré. Veuillez vous abonner.'}, status=status.HTTP_403_FORBIDDEN)
        except Abonnement.DoesNotExist:
            return Response({'error': 'Abonnement non trouvé.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'token': token.key,
            'role': getattr(user, 'role', None),  # Assurez-vous que le champ 'role' existe dans votre modèle utilisateur
            'last_login': user.last_login,
            'email': user.email,
        })

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Mettre à jour le champ last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Générer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)
        
        # Optionnel : connecter l'utilisateur
        login(request, user)
        
        return Response({
            'token': token.key,
            'role': getattr(user, 'role', None),  # Assurez-vous que le champ 'role' existe dans votre modèle utilisateur
            'last_login': user.last_login,
            'email': user.email,
            'user_id': user.pk,
            'username': user.username,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            # 'photo': user.photo,  # Décommentez si le champ 'photo' existe dans votre modèle utilisateur
        })

