# Standard Library Imports
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Django Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Django Models Imports
from django.db.models import Sum, F, Value, CharField, DecimalField, OuterRef, Subquery
from django.db.models.functions import Coalesce

# Third-Party Imports
from babel.dates import format_date
from dateutil.relativedelta import relativedelta

# DRF (Django REST Framework) Imports
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

# Application Imports
from .models import (
    Categorie, Categoriee, Categories, Entree, Depense, Investir, Abonnement, 
    Configabonnement, Presentation, Utilisateurs
)
from .forms import AbonnementForm, ConfigAbonForm, PresentationForm
from .serializers import (
    CategorieSerializer, CategorieeSerializer, CategoriesSerializer, 
    EntreeSerializer, DepenseSerializer, InvestirSerializer, 
    AbonnementSerializer, PresentationSerializer, UtilisateurSerializer
)
from Accounts.models import Utilisateurs

# DASH_____________________________________________________________________________________________________________________________________________
def menu(request):
    context = {
    }  
    return render(request, 'Pages/Log/menu.html', context)

# Stat

def courbe_transactions(request):
    # Comptage des utilisateurs par genre
    male_countens = Utilisateurs.objects.filter(sexe='Masculin', role='CLIENT').count()
    female_countens = Utilisateurs.objects.filter(sexe='Feminin', role='CLIENT').count()

    # Calcul des échéances
    date_today = datetime.now().date()
    date_un_mois_avant = date_today - timedelta(days=30)
    #echeances = Abonnement.objects.filter(date_fin__gte=date_un_mois_avant, date_fin__lte=date_today)
    # Étape 1 : Filtrer les utilisateurs avec le rôle 'CLIENT'
    clients = Utilisateurs.objects.filter(role='CLIENT')
    
    # Étape 2 : Obtenir les IDs de ces utilisateurs
    client_ids = clients.values_list('id', flat=True)
    
    # Étape 3 : Filtrer les abonnements pour ces utilisateurs
    echeances = Abonnement.objects.filter(utilisateur__in=client_ids)
    #echeances = Abonnement.objects.filter(date_fin__gte=date_un_mois_avant, date_fin__lte=date_today)
    total_echeances = echeances.count()
    echeances_payees = echeances.filter(est_actif=True).count()
    #echeances_non_payees = total_echeances - echeances_payees
    echeances_non_payees = echeances.filter(est_actif=False).count()

    # Comptage des transactions par type
    depot_count = Entree.objects.count()
    retrait_count = Depense.objects.count()

    # Somme des montants des transactions par type
    depot_amount = Entree.objects.aggregate(total=Sum('montant'))['total'] or 0
    retrait_amount = Depense.objects.aggregate(total=Sum('montant'))['total'] or 0

    # Transactions d'épargne pour le mois en cours
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    transactions = Entree.objects.filter(date__range=[first_day_of_month, last_day_of_month])

    # Organiser les transactions par date et par catégorie
    transactions_data = {}
    categories = set()
    categoriesd = set()  # Pour garder trace de toutes les catégories

    for transaction in transactions:
        date = transaction.date.strftime('%Y-%m-%d')
        if date not in transactions_data:
            transactions_data[date] = {}
        if transaction.categorie.nom not in transactions_data[date]:
            transactions_data[date][transaction.categorie.nom] = 0
        transactions_data[date][transaction.categorie.nom] += float(transaction.montant)
        categories.add(transaction.categorie.nom)

    # Transactions de prêt pour le mois précédent
    transactions_pret = Depense.objects.filter(date__gte=date_un_mois_avant)

    transactions_pret_data = {}
    for transaction in transactions_pret:
        date = transaction.date.strftime('%Y-%m-%d')
        if date not in transactions_pret_data:
            transactions_pret_data[date] = {}
        if transaction.categorie.nom not in transactions_pret_data[date]:
            transactions_pret_data[date][transaction.categorie.nom] = 0
        transactions_pret_data[date][transaction.categorie.nom] += float(transaction.montant)
        categoriesd.add(transaction.categorie.nom)

    context = {
        'male_countens': male_countens,
        'female_countens': female_countens,
        'echeances_payees': echeances_payees,
        'echeances_non_payees': echeances_non_payees,
        'depot_amount': depot_amount,
        'retrait_amount': retrait_amount,
        'depot_count': depot_count,
        'retrait_count': retrait_count,
        'transactions_data': transactions_data,
        'transactions_pret_data': transactions_pret_data,
        'categories': list(categories),
        'categoriesd': list(categoriesd),  # Passer la liste des catégories au template
    }

    return render(request, 'Pages/Dashboard/dashboard.html', context)

#___________________________________________________________________________________________________________________________________________
def courbe_transactionsclient(request, client_id):
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Comptage des transactions par type
    entrees = Entree.objects.filter(utilisateur=client_id, date__range=[first_day_of_month, last_day_of_month])
    depenses = Depense.objects.filter(utilisateur=client_id, date__range=[first_day_of_month, last_day_of_month])
            
    total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            
    remaining = total_entrees - total_depenses

    # Transactions d'épargne pour le mois en cours
    
    transactions = Entree.objects.filter(utilisateur=client_id,date__range=[first_day_of_month, last_day_of_month])

    # Organiser les transactions par date et par catégorie
    transactions_data = {}
    categories = set()
    categoriesd = set()  # Pour garder trace de toutes les catégories

    for transaction in transactions:
        date = transaction.date.strftime('%Y-%m-%d')
        if date not in transactions_data:
            transactions_data[date] = {}
        if transaction.categorie.nom not in transactions_data[date]:
            transactions_data[date][transaction.categorie.nom] = 0
        transactions_data[date][transaction.categorie.nom] += float(transaction.montant)
        categories.add(transaction.categorie.nom)

    # Transactions de prêt pour le mois précédent
    transactions_pret = Depense.objects.filter(utilisateur=client_id,date__range=[first_day_of_month, last_day_of_month])

    transactions_pret_data = {}
    for transaction in transactions_pret:
        date = transaction.date.strftime('%Y-%m-%d')
        if date not in transactions_pret_data:
            transactions_pret_data[date] = {}
        if transaction.categorie.nom not in transactions_pret_data[date]:
            transactions_pret_data[date][transaction.categorie.nom] = 0
        transactions_pret_data[date][transaction.categorie.nom] += float(transaction.montant)
        categoriesd.add(transaction.categorie.nom)

    context = {
        
        'total_entrees': total_entrees,
        'total_depenses': total_depenses,
        'remaining': remaining,
        'transactions_data': transactions_data,
        'transactions_pret_data': transactions_pret_data,
        'categories': list(categories),
        'categoriesd': list(categoriesd),  # Passer la liste des catégories au template
    }

    return render(request, 'Pages/Dashboard/dashboardcl.html', context)

# ABONNEMENTS_____________________________________________________________________________________________________________________________________________
def liste_abonnements(request):
    # Étape 1 : Filtrer les utilisateurs avec le rôle 'CLIENT'
    clients = Utilisateurs.objects.filter(role='CLIENT')
    
    # Étape 2 : Obtenir les IDs de ces utilisateurs
    client_ids = clients.values_list('id', flat=True)
    
    # Étape 3 : Filtrer les abonnements pour ces utilisateurs
    abonnements = Abonnement.objects.filter(utilisateur__in=client_ids)
    
    return render(request, 'Pages/Abonnements/liste_abonnements.html', {'abonnements': abonnements})

def detail_abonnements(request, client_id):
    # Récupérer le compte d'épargne en fonction de l'ID passé en paramètre
    abonnements = Abonnement.objects.filter(utilisateur=client_id)

    context = {
        'abonnements': abonnements,
    }

    return render(request, 'Pages/Abonnements/detail_abonnement.html', context)


# Vue pour modifier un configabon
def modifier_abonnements(request, pk):
    abonnements = get_object_or_404(Abonnement, pk=pk)
    if request.method == 'POST':
        form = AbonnementForm(request.POST, instance=abonnements)
        if form.is_valid():
            form.save()
            return redirect('liste_abonnements')
    else:
        form = AbonnementForm(instance=abonnements)
    return render(request, 'Pages/Abonnements/modifierabon.html', {'form': form})

def liste_configabon(request):
    abons = Configabonnement.objects.filter()
    return render(request, 'Pages/Abonnements/liste_config.html', {'abons': abons})

def modifier_configabon(request, pk):
    configabon= get_object_or_404(Configabonnement, pk=pk)
    if request.method == 'POST':
        form = ConfigAbonForm(request.POST, instance=configabon)
        if form.is_valid():
            montant = form.cleaned_data['montant']
            pourcentage = form.cleaned_data['pourcentage']
            # Recalculer les parts des actionnaires restants
            for abon in Abonnement.objects.all():
                abon.montant -= (montant * pourcentage) / 100
                abon.save()

            form.save()

            return redirect('liste_configabon')
    else:
        form = ConfigAbonForm(instance=configabon)
    return render(request, 'Pages/Abonnements/modifierconfigabon.html', {'form': form})

# ENTREES_____________________________________________________________________________________________________________________________________________
def liste_entrees(request, client_id):
    client = get_object_or_404(Utilisateurs, id=client_id)
    entrees = Entree.objects.filter(utilisateur=client)

    return render(request, 'Pages/Clients/liste_entrees.html', {'entrees': entrees})


# DEPENSES_____________________________________________________________________________________________________________________________________________
def liste_depenses(request, client_id):
    client = get_object_or_404(Utilisateurs, id=client_id)
    depenses = Depense.objects.filter(utilisateur=client)

    return render(request, 'Pages/Clients/liste_depenses.html', {'depenses': depenses})

# PRESENTATION_____________________________________________________________________________________________________________________________________________
def liste_presentation(request):
    presents = Presentation.objects.filter()
    return render(request, 'Pages/Presentations/liste_presentation.html', {'presents': presents})

# Vue pour creer une PresentationForm
def create_presentation(request):
    if request.method == 'POST':
        form = PresentationForm(request.POST, request.FILES)
        if form.is_valid():
        # Enregistrement du formulaire
            form.save()

            # Redirection après création
            return redirect('liste_presentation')
        else:
            # Si le formulaire n'est pas valide, imprime les erreurs
            print("Formulaire invalide :", form.errors)
    else:
        form = PresentationForm()
    
    return render(request, 'Pages/Presentations/create_presentation.html', {'form': form})

def modifier_presentation(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    if request.method == 'POST':
        form = PresentationForm(request.POST, request.FILES, instance=presentation)
        if form.is_valid():
            form.save()
            return redirect('liste_presentation')
    else:
        form = PresentationForm(instance=presentation)
    
    return render(request, 'Pages/Presentations/create_presentation.html', {'form': form})








# ___________________________________________________________________ MOBILE  __________________________________________________________________________

class AbonnementDetailView(generics.RetrieveAPIView):
    serializer_class = AbonnementSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        utilisateur = self.request.user
        # Récupère l'abonnement actif de l'utilisateur connecté
        abonnement = Abonnement.objects.filter(utilisateur=utilisateur).first()
        #abonnement = Abonnement.objects.filter(utilisateur=utilisateur, est_actif=True).first()
        if abonnement:
            return abonnement
        else:
            raise Http404("Abonnement non trouvé")

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class EntreeViewSet(viewsets.ModelViewSet):
    queryset = Entree.objects.all()
    serializer_class = EntreeSerializer

class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer

class AbonnementViewSet(viewsets.ModelViewSet):
    queryset = Abonnement.objects.all()
    serializer_class = AbonnementSerializer


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateurs.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        user = Utilisateurs.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class EntreeViewSet(viewsets.ModelViewSet):
    queryset = Entree.objects.all()
    serializer_class = EntreeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#STATISQUES __________________________________________________________________________________________________

class StatsViewbon(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()

        def calculate_stats(start_date, end_date):
            entrees = Entree.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            depenses = Depense.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            
            total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
            total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            
            remaining = total_entrees - total_depenses
            
            depense_categories = depenses.values('categorie').annotate(total=Sum('montant')).order_by('-total')
            percentage_by_category = {item['categorie']: (item['total'] / total_depenses * 100) if total_depenses > 0 else 0 for item in depense_categories}
            
            return {
                'total_entrees': total_entrees,
                'total_depenses': total_depenses,
                'remaining': remaining,
                'percentage_depenses': (total_depenses / total_entrees * 100) if total_entrees > 0 else 0,
                'percentage_by_category': percentage_by_category
            }

        # Dates pour les totaux mensuels, trimestriels et annuels
        start_month = now.replace(day=1)
        end_month = (start_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        start_quarter = (now - timedelta(days=now.month % 3 * 30)).replace(day=1)
        end_quarter = (start_quarter + timedelta(days=92)).replace(day=1) - timedelta(seconds=1)
        start_year = now.replace(month=1, day=1)
        end_year = start_year.replace(year=now.year + 1) - timedelta(seconds=1)

        response_data = {
            'monthly': calculate_stats(start_month, end_month),
            'quarterly': calculate_stats(start_quarter, end_quarter),
            'yearly': calculate_stats(start_year, end_year)
        }

        return Response(response_data, status=status.HTTP_200_OK)

# STAT ORDINAIRES____________________________________________________________________________________________________________________________

class StatsViewtrisordinaire(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()

        def calculate_stats(start_date, end_date):
            entrees = Entree.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            depenses = Depense.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            
            total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
            total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            
            remaining = total_entrees - total_depenses
            
            depense_categories = depenses.values('categorie').annotate(total=Sum('montant')).order_by('-total')
            percentage_by_category = {item['categorie']: (item['total'] / total_depenses * 100) if total_depenses > 0 else 0 for item in depense_categories}
            
            return {
                'total_entrees': total_entrees,
                'total_depenses': total_depenses,
                'remaining': remaining,
                'percentage_depenses': (total_depenses / total_entrees * 100) if total_entrees > 0 else 0,
                'percentage_by_category': percentage_by_category
            }

        # Dates pour les totaux annuels et trimestriels
        start_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        # Calculer les dates pour chaque trimestre
        quarters = [
            (start_year.replace(month=1, day=1), start_year.replace(month=3, day=31, hour=23, minute=59, second=59, microsecond=999999)),
            (start_year.replace(month=4, day=1), start_year.replace(month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)),
            (start_year.replace(month=7, day=1), start_year.replace(month=9, day=30, hour=23, minute=59, second=59, microsecond=999999)),
            (start_year.replace(month=10, day=1), start_year.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)),
        ]

        response_data = {
            'annual': calculate_stats(start_year, end_year),
            'quarterly': {
                f'Q{i+1}': calculate_stats(start, end) for i, (start, end) in enumerate(quarters)
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

# AFFICHAGE----------------------------------------------
class StatsViewsanscalenntre(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()

        # Date d'abonnement de l'utilisateur
        abon = Abonnement.objects.filter(utilisateur=user).first()
        if not abon:
            return Response({"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)
        date_abonnement = abon.date_debut

        def calculate_stats(start_date, end_date):
            entrees = Entree.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            depenses = Depense.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            
            total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
            total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            
            remaining = total_entrees - total_depenses
            
            depense_categories = depenses.values('categorie').annotate(total=Sum('montant')).order_by('-total')
            percentage_by_category = {item['categorie']: (item['total'] / total_depenses * 100) if total_depenses > 0 else 0 for item in depense_categories}
            
            return {
                'total_entrees': total_entrees,
                'total_depenses': total_depenses,
                'remaining': remaining,
                'percentage_depenses': (total_depenses / total_entrees * 100) if total_entrees > 0 else 0,
                'percentage_by_category': percentage_by_category
            }

        # Dates pour chaque mois de l'année à partir de la date d'abonnement
        monthly_stats = []
        for month in range(12):
            start_month = (date_abonnement + timedelta(days=month*30)).replace(day=1)
            end_month = (start_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            stats = calculate_stats(start_month, end_month)
            stats['month_year'] = format_date(start_month, format='MMMM yyyy', locale='fr_FR')
            monthly_stats.append(stats)

        # Calcul des statistiques trimestrielles
        start_quarter = date_abonnement.replace(day=1)
        end_quarter = (start_quarter + timedelta(days=92)).replace(day=1) - timedelta(seconds=1)
        quarterly_stats = calculate_stats(start_quarter, end_quarter)
        
        # Calcul des statistiques annuelles
        start_year = date_abonnement.replace(day=1)
        end_year = start_year.replace(year=date_abonnement.year + 1) - timedelta(seconds=1)
        yearly_stats = calculate_stats(start_year, end_year)

        response_data = {
            'monthly': monthly_stats,
            'quarterly': quarterly_stats,
            'yearly': yearly_stats
        }

        return Response(response_data, status=status.HTTP_200_OK)


# AFFICHAGE RECAP DE ENTREES ET DEPENSES SYNTHESE ___________________________________________________________________________________________________________________

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()
        #month = format_date(now, format='MMMM', locale='fr_FR').encode('utf-8').decode('utf-8')
        #month = format_date(today, format='MMMM', locale='fr_FR')
        month = now.month
        year = now.year
        # Date d'abonnement de l'utilisateur
        abon = Abonnement.objects.filter(utilisateur=user).first()
        if not abon:
            return Response({"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)
        date_abonnement = abon.date_debut

        def calculate_stats(start_date, end_date):
            entrees = Entree.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            depenses = Depense.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            investirs = Investir.objects.filter(utilisateur=user, date__range=[start_date, end_date])
            
            total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
            #total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            total_depenses = (depenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)

            remaining = total_entrees - total_depenses
            
            entree_categories = entrees.values('categorie__nom').annotate(total=Sum('montant')).order_by('-total')
            #percentage_entrees_by_category = {item['categorie__nom']: (item['total'] / total_entrees * 100) if total_entrees > 0 else 0 for item in entree_categories}
            percentage_entrees_by_category = {
                    item['categorie__nom']: {
                        'total': item['total'],
                        'percentage': (item['total'] / total_entrees * 100) if total_entrees > 0 else 0
                    }
                    for item in entree_categories
                }


            #depense_categories = depenses.values('categorie__nom').annotate(total=Sum('montant')).order_by('-total')
            #investir_categories = investirs.values('categorie__nom').annotate(total=Sum('montant')).order_by('-total')
            #percentage_depenses_by_category = {item['categorie__nom']: (item['total'] / total_depenses * 100) if total_depenses > 0 else 0 for item in depense_categories and investir_categories }
           
            # Récupération des catégories et montants pour les dépenses
            depense_categories = depenses.values('categorie__nom').annotate(total=Sum('montant')).order_by('-total')

            # Récupération des catégories et montants pour les investissements
            investir_categories = investirs.values('categorie__nom').annotate(total=Sum('montant')).order_by('-total')

            # Fusionner les deux catégories en additionnant les montants
            combined_categories = defaultdict(Decimal)  # Utiliser Decimal pour correspondre au type de montant

            for item in depense_categories:
                combined_categories[item['categorie__nom']] += item['total']

            for item in investir_categories:
                combined_categories[item['categorie__nom']] += item['total']

            # Calculer le pourcentage de chaque catégorie par rapport au total des dépenses
            percentage_depenses_by_category = {
                #category: (total / Decimal(total_depenses) * 100) if total_depenses > 0 else 0
                category: {
                    'total': total,
                    'percentage': (total / Decimal(total_depenses) * 100) if total_depenses > 0 else 0
                }
                for category, total in combined_categories.items()
            }


            return {
                'total_entrees': total_entrees,
                'total_depenses': total_depenses,
                'remaining': remaining,
                'percentage_depenses': (total_depenses / total_entrees * 100) if total_entrees > 0 else 0,
                'percentage_entrees_by_category': percentage_entrees_by_category,
                'percentage_depenses_by_category': percentage_depenses_by_category,
                'month' : month,
                'year' : year  # Ajout de la liste des transactions
            }


        
        # Dates pour chaque mois de l'année à partir de la date d'abonnement
        # Obtenir le mois actuel
    # Crée une date spécifique : 1er février 2025
        #specific_date = datetime(2025, 2, 1)

    # Si vous voulez traiter cette date comme une date avec fuseau horaire, vous pouvez la convertir
        #today = timezone.make_aware(specific_date, timezone.get_current_timezone())
        today = datetime.today()
        current_month = today.month
        current_year = today.year

        # Dates pour chaque mois de l'année à partir de la date d'abonnement
        monthly_stats = []
        current_date = date_abonnement
        for month in range(12):
            start_month = current_date.replace(day=1)
            end_month = (start_month + relativedelta(months=1)) - timedelta(seconds=1)
            stats = calculate_stats(start_month, end_month)
            stats['month'] = format_date(start_month, format='MMMM', locale='fr_FR').encode('utf-8').decode('utf-8')
            stats['year'] = start_month.year
            monthly_stats.append(stats)
            current_date = start_month + relativedelta(months=1)

        # Trier les statistiques mensuelles pour commencer par le mois actuel
        # Trouver l'index du mois actuel
        current_month_name = format_date(today.replace(day=1), format='MMMM', locale='fr_FR').encode('utf-8').decode('utf-8')
        current_month_index = next((index for (index, d) in enumerate(monthly_stats) if d["month"] == current_month_name), None)

        # Réorganiser la liste pour commencer par le mois actuel
        if current_month_index is not None:
            monthly_stats = monthly_stats[current_month_index:] + monthly_stats[:current_month_index]

    # Calcul des statistiques trimestrielles
        #start_quarter = date_abonnement.replace(day=1)
        #end_quarter = (start_quarter + relativedelta(months=3)) - timedelta(seconds=1)
        #quarterly_stats = calculate_stats(start_quarter, end_quarter)
    # Initialisation des statistiques trimestrielles
        # Date actuelle
        # Calcul des statistiques trimestrielles pour le trimestre actuel
        # La date actuelle
        today = timezone.now()

        # Trouver le trimestre actuel par rapport à la date d'abonnement
        months_since_abonnement = (today.year - date_abonnement.year) * 12 + today.month - date_abonnement.month
        current_quarter_start_month = (months_since_abonnement // 3) * 3 + date_abonnement.month

        # Ajuster pour ne pas dépasser décembre
        if current_quarter_start_month > 12:
            current_quarter_start_month -= 12
            start_quarter_year = date_abonnement.year + 1
        else:
            start_quarter_year = date_abonnement.year

        start_quarter = date_abonnement.replace(month=current_quarter_start_month, year=start_quarter_year, day=1)
        end_quarter = (start_quarter + relativedelta(months=3)) - timedelta(seconds=1)

        # Calcul des statistiques pour le trimestre actuel
        quarterly_stats = calculate_stats(start_quarter, end_quarter)
        

        # Calcul des statistiques annuelles
        start_year = date_abonnement.replace(day=1)
        end_year = start_year.replace(year=date_abonnement.year + 1) - timedelta(seconds=1)
        yearly_stats = calculate_stats(start_year, end_year)

        
        response_data = {
            'monthly': monthly_stats,
            'quarterly': quarterly_stats,
            #'quarterly':current_quarter_stats,
            'yearly': yearly_stats,
            'month' : month,
            'year' : year  # Ajout de la liste des transactions
        }

        return Response(response_data, status=status.HTTP_200_OK)



# _____________________________________________________________________________________________________________________________________________________    


# LISTE DES ENTREES ET DEPENSES DU MOIS DE L'UTILISATEUR ACCUEIL _________________________________________________________________________

class ClientTransBudgetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        utilisateur = request.user
        print(f'Utilisateur authentifié: {utilisateur}')  # Ajout de logs pour le débogage

        # Définir les dates de début et de fin pour le mois en cours
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
        
        # Récupérer les entrées et les dépenses de l'utilisateur connecté pour le mois en cours
        entrees = Entree.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        depenses = Depense.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        investirs = Investir.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])

        # Calculer les sommes pour le mois en cours
        total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
        total_investirs = investirs.aggregate(Sum('montant'))['montant__sum'] or 0
        total_depenses = (depenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)
        reste = total_entrees - total_depenses

        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        entreesday = Entree.objects.filter(utilisateur=utilisateur, date__range=[start_of_day, end_of_day])
        depensesday = Depense.objects.filter(utilisateur=utilisateur, date__range=[start_of_day, end_of_day])
        investirsday = Investir.objects.filter(utilisateur=utilisateur, date__range=[start_of_day, end_of_day])


        # Récupérer l'abonnement de l'utilisateur
        abonnement = Abonnement.objects.filter(utilisateur=utilisateur, est_actif=True).values(
            'date_debut', 'date_fin', 'est_actif','nature'
        ).first()

        # Créer la liste commune des entrées et des dépenses
        entrees_list = list(
            entreesday.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('entree', output_field=CharField()))
        )
        depenses_list = list(
            depensesday.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('depense', output_field=CharField()))
        )
        investirs_list = list(
            investirsday.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('depense', output_field=CharField()))
        )

        # Fusionner les listes d'entrées et de dépenses
        transactions = entrees_list + depenses_list + investirs_list

        # Trier la liste par date
        transactions.sort(key=lambda x: x['date'])

        top_transactions = transactions[:3]

        #month = format_date(today, format='MMMM', locale='fr_FR').encode('utf-8').decode('utf-8')
        month = format_date(today, format='MMMM', locale='fr_FR')
        year = today.year

        # Créer la réponse
        resultats = {
            'total_entrees': total_entrees,
            'total_depenses': total_depenses,
            'reste': reste,
            'abonnement': abonnement,
            #'transactions': transactions,
            'transactions': top_transactions,
            'month' : month,
            'year' : year  # Ajout de la liste des transactions
        }

        return Response(resultats)
# ________________________________________________________________________________________________________________________________________________________________


# LISTE DES ENTREES DU MOIS DE L'UTILISATEUR ACCUEIL _______________________________________________________________________   

class ClientTransEntreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        utilisateur = request.user
        print(f'Utilisateur authentifié: {utilisateur}')  # Ajout de logs pour le débogage

        # Définir les dates de début et de fin pour le mois en cours
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Vérifier l'abonnement de l'utilisateur
        today_date = timezone.now().date()
        try:
            abonnement = Abonnement.objects.get(utilisateur=utilisateur)
            if abonnement.date_fin < today_date:
                return Response({'message': 'Abonnement expiré. Veuillez vous abonner.'})
        except Abonnement.DoesNotExist:
            abonnement = None

        # Récupérer les entrées et les dépenses de l'utilisateur connecté pour le mois en cours
        entrees = Entree.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        depenses = Depense.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        investirs = Investir.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])

        # Calculer les sommes pour le mois en cours
        total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
        total_investirs = investirs.aggregate(Sum('montant'))['montant__sum'] or 0
        total_depenses = (depenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)
        reste = total_entrees - total_depenses

        # Calculer les entrées par catégorie
        entrees_par_categorie = entrees.values('categorie__id').annotate(total=Sum('montant', output_field=DecimalField()))

        # Récupérer les catégories
        categories = Categoriee.objects.all()

        # Faire une jointure gauche entre les catégories et les totaux des entrées
        categories_avec_totaux = categories.annotate(
            total=Coalesce(
                Subquery(
                    entrees_par_categorie.filter(categorie__id=OuterRef('id')).values('total')[:1]
                ),
                Value(0, output_field=DecimalField())
            )
        ).order_by('-total')

        # Optionnel : si vous avez besoin des noms des catégories
        entrees_par_categorie_final = categories_avec_totaux.values('nom', 'total','id')

        # Calculer les dépenses par catégorie
        depenses_par_categorie = depenses.values('categorie__nom', 'categorie__id').annotate(total=Sum('montant')).order_by('-total')

        categories = Categoriee.objects.all()
        serializer = CategorieeSerializer(categories, many=True)

        # Créer la liste commune des entrées et des dépenses
        entrees_list = list(
            entrees.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('entree', output_field=CharField()))
        )
        depenses_list = list(
            depenses.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('depense', output_field=CharField()))
        )

        # Fusionner les listes d'entrées et de dépenses
        transactions = entrees_list + depenses_list

        # Trier la liste par date
        transactions.sort(key=lambda x: x['date'])

        # Sérialiser l'abonnement
        abonnement_data = AbonnementSerializer(abonnement).data if abonnement else None

        month = format_date(today, format='MMMM', locale='fr_FR')
        year = today.year

        # Créer la réponse
        resultats = {
            'total_entrees': total_entrees,
            'total_depenses': total_depenses,
            'reste': reste,
            'abonnement': abonnement_data,
            'entrees_par_categorie': list(entrees_par_categorie_final),  # Ajout des entrées par catégorie
            'depenses_par_categorie': list(depenses_par_categorie),  # Ajout des dépenses par catégorie
            'transactions': transactions,  # Ajout de la liste des transactions
            'cat': list(serializer.data),
            'month' : month,
            'year' : year
        }

        return Response(resultats)

#____________________________________________________________________________________________________________________________________________ 


# LISTE DES DEPENSES DU MOIS DE L'UTILISATEUR ACCUEIL _________________________________________________________________________

class ClientTransDepenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        utilisateur = request.user
        print(f'Utilisateur authentifié: {utilisateur}')  # Ajout de logs pour le débogage

        # Définir les dates de début et de fin pour le mois en cours
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Vérifier l'abonnement de l'utilisateur
        today_date = timezone.now().date()
        try:
            abonnement = Abonnement.objects.get(utilisateur=utilisateur)
            if abonnement.date_fin < today_date:
                return Response({'message': 'Abonnement expiré. Veuillez vous abonner.'})
        except Abonnement.DoesNotExist:
            abonnement = None

        # Récupérer les entrées et les dépenses de l'utilisateur connecté pour le mois en cours
        entrees = Entree.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        depenses = Depense.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        investirs = Investir.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])

        # Calculer les sommes pour le mois en cours
        total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
        total_investirs = investirs.aggregate(Sum('montant'))['montant__sum'] or 0
        total_depenses = (depenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)
        reste = total_entrees - total_depenses

        # Calculer les depenses par catégorie
        depenses_par_categorie = depenses.values('categorie__id').annotate(total=Sum('montant', output_field=DecimalField()))

        # Récupérer les catégories
        categories = Categorie.objects.all()

        # Faire une jointure gauche entre les catégories et les totaux des entrées
        categories_avec_totaux = categories.annotate(
            total=Coalesce(
                Subquery(
                    depenses_par_categorie.filter(categorie__id=OuterRef('id')).values('total')[:1]
                ),
                Value(0, output_field=DecimalField())
            )
        ).order_by('-total')

        # Optionnel : si vous avez besoin des noms des catégories
        depenses_par_categorie_final = categories_avec_totaux.values('nom', 'total','id')

        # Calculer les dépenses par catégorie
        depenses_par_categorie = depenses.values('categorie__nom', 'categorie__id').annotate(total=Sum('montant')).order_by('-total')

        categories = Categorie.objects.all()
        serializer = CategorieSerializer(categories, many=True)

        # Créer la liste commune des entrées et des dépenses
        entrees_list = list(
            entrees.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('entree', output_field=CharField()))
        )
        depenses_list = list(
            depenses.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('depense', output_field=CharField()))
        )

        # Fusionner les listes d'entrées et de dépenses
        transactions = entrees_list + depenses_list

        # Trier la liste par date
        transactions.sort(key=lambda x: x['date'])

        # Sérialiser l'abonnement
        abonnement_data = AbonnementSerializer(abonnement).data if abonnement else None

        month = format_date(today, format='MMMM', locale='fr_FR')
        year = today.year

        # Créer la réponse
        resultats = {
            'total_entrees': total_entrees,
            'total_depenses': total_depenses,
            'reste': reste,
            'abonnement': abonnement_data,
            'entrees_par_categorie': list(depenses_par_categorie),  # Ajout des entrées par catégorie
            'depenses_par_categorie': list(depenses_par_categorie_final),  # Ajout des dépenses par catégorie
            'transactions': transactions,  # Ajout de la liste des transactions
            'cat': list(serializer.data),
            'month' : month,
            'year' : year
        }

        return Response(resultats)

# LISTE DES INVESTISSEMENTS DU MOIS DE L'UTILISATEUR ACCUEIL _________________________________________________________________________
class ClientTransInvestirView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        utilisateur = request.user
        print(f'Utilisateur authentifié: {utilisateur}')  # Ajout de logs pour le débogage

        # Définir les dates de début et de fin pour le mois en cours
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Vérifier l'abonnement de l'utilisateur
        today_date = timezone.now().date()
        try:
            abonnement = Abonnement.objects.get(utilisateur=utilisateur)
            if abonnement.date_fin < today_date:
                return Response({'message': 'Abonnement expiré. Veuillez vous abonner.'})
        except Abonnement.DoesNotExist:
            abonnement = None

        # Récupérer les entrées et les dépenses de l'utilisateur connecté pour le mois en cours
        entrees = Entree.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        depenses = Depense.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])
        investirs = Investir.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month])

        # Calculer les sommes pour le mois en cours
        total_entrees = entrees.aggregate(Sum('montant'))['montant__sum'] or 0
        total_investirs = investirs.aggregate(Sum('montant'))['montant__sum'] or 0
        total_depenses = (depenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)
        reste = total_entrees - total_depenses

        # Calculer les depenses par catégorie
        investirs_par_categorie = investirs.values('categorie__id').annotate(total=Sum('montant', output_field=DecimalField()))

        # Récupérer les catégories
        categories = Categories.objects.all()

        # Faire une jointure gauche entre les catégories et les totaux des entrées
        categories_avec_totaux = categories.annotate(
            total=Coalesce(
                Subquery(
                    investirs_par_categorie.filter(categorie__id=OuterRef('id')).values('total')[:1]
                ),
                Value(0, output_field=DecimalField())
            )
        ).order_by('-total')

        # Optionnel : si vous avez besoin des noms des catégories
        investirs_par_categorie_final = categories_avec_totaux.values('nom', 'total','id')

        # Calculer les dépenses par catégorie
        investirs_par_categorie = investirs.values('categorie__nom', 'categorie__id').annotate(total=Sum('montant')).order_by('-total')

        categories = Categories.objects.all()
        serializer = CategoriesSerializer(categories, many=True)

        # Créer la liste commune des entrées et des dépenses
        entrees_list = list(
            entrees.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('entree', output_field=CharField()))
        )
        depenses_list = list(
            depenses.values('date', 'categorie__nom', 'montant')
            .annotate(type=Value('depense', output_field=CharField()))
        )

        # Fusionner les listes d'entrées et de dépenses
        transactions = entrees_list + depenses_list

        # Trier la liste par date
        transactions.sort(key=lambda x: x['date'])

        # Sérialiser l'abonnement
        abonnement_data = AbonnementSerializer(abonnement).data if abonnement else None

        #month = format_date(today, format='MMMM', locale='fr_FR')
        month = format_date(today, format='MMMM', locale='fr_FR')
        year = today.year

        # Créer la réponse
        resultats = {
            'total_entrees': total_entrees,
            'total_depenses': total_depenses,
            'reste': reste,
            'abonnement': abonnement_data,
            'entrees_par_categorie': list(investirs_par_categorie),  # Ajout des entrées par catégorie
            'depenses_par_categorie': list(investirs_par_categorie_final),  # Ajout des dépenses par catégorie
            'transactions': transactions,  # Ajout de la liste des transactions
            'cat': list(serializer.data),
            'month' : month,
            'year' : year
        }

        return Response(resultats)

# ____________________________________________________________________________________________________________________________________________________________


# ENREGISTREMENT DES ENTREES ET DEPENSES PAR MODAL______________________________________________________________________________________________________________________________

logger = logging.getLogger(__name__)

class EntreeViewSett(viewsets.ModelViewSet):
    queryset = Entree.objects.all()
    serializer_class = EntreeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        logger.error(f"Entree creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


logger = logging.getLogger(__name__)

class DepenseViewSett(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        logger.error(f"Entree creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



logger = logging.getLogger(__name__)

class InvestirViewSett(viewsets.ModelViewSet):
    queryset = Investir.objects.all()
    serializer_class = InvestirSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        logger.error(f"Entree creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# _______________________________________________________________________________________________________________________________________________________________

# AFFICHER LES ENTREES ET DEPENSES_________ POUR LES SUPPRIMER __________________________________________________________________________________________________

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_transactions(request):
    utilisateur = request.user
    print(f'Utilisateur authentifié: {utilisateur}')  # Ajout de logs pour le débogage

    # Définir les dates de début et de fin pour le mois en cours
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

    # Récupérer les entrées et les dépenses de l'utilisateur connecté pour le mois en cours
    entrees = Entree.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month]).values('id', 'categorie__nom', 'date', 'montant')
    depenses = Depense.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month]).values('id', 'categorie__nom', 'date', 'montant')
    investirs = Investir.objects.filter(utilisateur=utilisateur, date__range=[first_day_of_month, last_day_of_month]).values('id', 'categorie__nom', 'date', 'montant')

    return JsonResponse({'entrees': list(entrees), 'depenses': list(depenses) + list(investirs)})
    #return JsonResponse({'entrees': list(entrees), 'depenses': list(depenses)})

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction(request, transaction_id, transaction_type):
    if transaction_type == 'entree':
        transaction = get_object_or_404(Entree, id=transaction_id, utilisateur=request.user)
    else:
        transaction = get_object_or_404(Depense, id=transaction_id, utilisateur=request.user)
    transaction.delete()
    return JsonResponse({'success': True})
#__________________________________________________________________________________________________________________________________________________________________


# AFFICHER LE TABLEAU DE BORD____________________________________________________________________________________________________________________________________

from itertools import chain
@api_view(['GET'])
def monthly_summary(request):
    user = request.user  # Assuming user is authenticated and user info is available
    
    # Current month
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=31)).replace(day=1)  # Start of next month
    
    # Entrees
    entries = Entree.objects.filter(utilisateur=user, date__range=[start_date, end_date])
    total_entries = entries.aggregate(total=Sum('montant'))['total'] or 0.0  # Ensure it's a float
    
    # Dépenses
    expenses = Depense.objects.filter(utilisateur=user, date__range=[start_date, end_date])
    investirs = Investir.objects.filter(utilisateur=user, date__range=[start_date, end_date])
    #total_expenses = expenses.aggregate(total=Sum('montant'))['total'] + investirs.aggregate(total=Sum('montant'))['total'] or 0.0  # Ensure it's a float
    total_expenses = (expenses.aggregate(Sum('montant'))['montant__sum'] or 0) + (investirs.aggregate(Sum('montant'))['montant__sum'] or 0)

    # Transactions récentes
    recent_transactions = list(
        Entree.objects.filter(utilisateur=user).values('categorie__nom', 'montant')[:5]
    ) 
    
    #recent_transactionss =list(
    #    Depense.objects.filter(utilisateur=user).values('categorie__nom', 'montant')[:5]
    #)
    # Combine les résultats des deux requêtes
    recent_depenses = Depense.objects.filter(utilisateur=user).values('categorie__nom', 'montant')[:5]
    recent_investissements = Investir.objects.filter(utilisateur=user).values('categorie__nom', 'montant')[:5]

    recent_transactionss = list(chain(recent_depenses, recent_investissements))

    return JsonResponse({
        'total_entries': float(total_entries),
        'total_expenses': float(total_expenses),
        'recent_transactions': recent_transactions,
        'recent_transactionss': recent_transactionss
    })

#______________________________________________________________________________________________________________________________________________________________
from django.http import JsonResponse, HttpResponseNotFound
from .models import Abonnement

def get_subscription_details(request, subscription_id):
    try:
        abonnement = Abonnement.objects.get(id=subscription_id)
        data = {
            'est_actif': abonnement.est_actif,
            'date_fin': abonnement.date_fin,
            'nature': abonnement.nature,
        }
        return JsonResponse(data)
    except Abonnement.DoesNotExist:
        return HttpResponseNotFound('Abonnement non trouvé')

# PRESENTATION PAGE_________________________________________________________________________________________________________________________________________________________________
from rest_framework.permissions import AllowAny

class PresentationAPIView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        # Suppose we have only one presentation data entry
        presentation_data = Presentation.objects.first()
        if presentation_data:
            serializer = PresentationSerializer(presentation_data)
            return Response(serializer.data)
        else:
            return Response({"error": "No presentation data found"}, status=404)

#__ABONNEMENT LORS DE L'INSCRIPTION _______________________________________________________________________________________________________________________________________
def config_abonnement(request):
    # Récupère la dernière configuration disponible
    config = Configabonnement.objects.order_by('-date').first()
    if config:
        data = {
            'montant': str(config.montant),
            'pourcentage': str(config.pourcentage),
            'date': config.date.isoformat(),  # Assurez-vous que la date est formatée correctement
        }
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Aucune configuration trouvée'}, status=404)

# MODIFIER PHOTO DE PROFIL____________________________________________________________________________________________________________________________________________________


@login_required
@csrf_exempt
def upload_image(request):
    print(f"Requête reçue pour upload_image avec méthode: {request.method}")  # Affiche la méthode de la requête
    if request.method == 'POST':
        try:
            file = request.FILES.get('file')
            if file:
                user = request.user
                print(f"Utilisateur connecté: {user.username}")  # Affiche le nom d'utilisateur
                user.photo.save(file.name, file, save=True)
                return JsonResponse({'status': 'success', 'message': 'Image téléchargée avec succès'})
            else:
                return JsonResponse({'status': 'failure', 'message': 'Aucun fichier reçu'}, status=400)
        except Exception as e:
            print(f"Erreur lors du téléchargement de l'image: {str(e)}")  # Affiche les erreurs
            return JsonResponse({'status': 'failure', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'failure', 'message': 'Méthode non autorisée'}, status=405)


#________________________________________________________________________ BACK OFFICE ______________________________________________________________________________________

#_________________________________________________________________________________________________________________________________________________________________

#________________________________________________________________________________________________________________________________________________________

#______________________________________________________________________________________________________________________________________________________________