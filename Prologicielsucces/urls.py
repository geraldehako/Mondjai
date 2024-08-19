from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Accounts.views import supprimer_client,modifier_utilisateur,logout_user,login_user,supprimer_utilisateur,CustomAuthToken, get_csrf_token, logout_userbank,  register, edit_profile,liste_client,change_usernamecl,change_passwordcl,liste_utilisateur,create_utilisateur
#from Gestions.serializers import AbonnementDetailView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from Gestions.views import modifier_configabon,liste_presentation,liste_configabon,modifier_abonnements,courbe_transactionsclient,courbe_transactions,menu,liste_abonnements,liste_depenses,liste_entrees,detail_abonnements,AbonnementDetailView, ClientTransBudgetView, DepenseViewSett, EntreeViewSett, StatsView, UtilisateurViewSet, EntreeViewSet, DepenseViewSet,InvestirViewSett, ClientTransEntreeView,PresentationAPIView,ClientTransDepenseView,ClientTransInvestirView, delete_transaction, get_all_transactions, monthly_summary,liste_abonnements
from Gestions.views import create_presentation,config_abonnement,modifier_presentation,upload_image
# Créer un routeur par défaut
router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet, basename='utilisateurs')
router.register(r'entrees', EntreeViewSet, basename='entree')
router.register(r'depenses', DepenseViewSet, basename='depense')

urlpatterns = [

# BACK OFFICE______________________________________________________________________________________________

    # URL pour authentification
    path('', login_user, name='login'),
    path('accounts/log', logout_user, name='signup'),
    path('administration/menu', menu, name='menu'),
    path('courbe_transactions/', courbe_transactions, name='courbe_transactions'),

    # URL pour la liste des clients
    path('clients/', liste_client, name='liste_clients'),
    path('courbe_transactionsclient/<int:client_id>/', courbe_transactionsclient, name='courbe_transactionsclient'),
    path('detail_abonnement/<int:client_id>/', detail_abonnements, name='detail_abonnement'),
    path('entree_client/<int:client_id>/', liste_entrees, name='entree_client'),
    path('depense_client/<int:client_id>/', liste_depenses, name='depense_client'),
    path('modifier_utilisateur/<int:client_id>/', modifier_utilisateur, name='modifier_utilisateur'),
    path('supprimer_client/<int:client_id>/', supprimer_client, name='supprimer_client'),

    # URL pour utlisateur
    path('gestionnaires/', liste_utilisateur, name='liste_gestionnaires'),
    path('gestionnaires/create/', create_utilisateur, name='create_utilisateur'),
    path('change-usernamecl/<int:idact>/', change_usernamecl, name='change_usernamecl'),
    path('change-passwordcl/<int:idact>/', change_passwordcl, name='change_passwordcl'),
    path('supprimer_user/<int:client_id>/', supprimer_utilisateur, name='supprimer_user'),

    # URL pour la liste des abonnements
    path('abonnements/', liste_abonnements, name='liste_abonnements'),
    path('modifier_abon/<int:pk>/', modifier_abonnements, name='modifier_abonnements'),

     # URL pour la liste des configuration abonnements
    path('liste_configabon/', liste_configabon, name='liste_configabon'),
    path('modifier_configabon/<int:pk>/', modifier_configabon, name='modifier_configabon'),

    # URL pour la liste des presentations
    path('presentations/', liste_presentation, name='liste_presentation'),
    path('presentations/create/', create_presentation, name='create_presentation'),
    path('presentations/<int:pk>/m/', modifier_presentation, name='modifier_presentation'),

# MOBILE______________________________________________________________________________________________
    path('admin/', admin.site.urls),
    path('logout_userbank', logout_userbank, name='logout_userbank'),
    path('register/', register, name='register'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    #path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('api/', include(router.urls)),  # Inclure les routes du routeur
    path('entree/', EntreeViewSet.as_view({'post': 'create'}), name='entree-create'),
    path('depense/', DepenseViewSet.as_view({'post': 'create'}), name='depense-create'),

    # AFFICHER LES STATISQUES______________________________________________________________________________________________
    path('stats/', StatsView.as_view(), name='stats'),
    path('client_trans_budget/', ClientTransBudgetView.as_view(), name='client_trans_budget'),
    path('client_trans_entree/', ClientTransEntreeView.as_view(), name='client_trans_entree'),
    path('client_trans_depense/', ClientTransDepenseView.as_view(), name='client_trans_depense'),
    path('client_trans_investir/', ClientTransInvestirView.as_view(), name='client_trans_investir'),

    # ENREGISTREMENT DES LIGNES ___________________________________________________________________________________________
    path('client_entree/', EntreeViewSett.as_view({'post': 'create'}), name='client_entree'),
    path('client_depense/', DepenseViewSett.as_view({'post': 'create'}), name='client_depense'),
    path('client_investir/', InvestirViewSett.as_view({'post': 'create'}), name='client_investir'),

    # AFFICHER LES ENTREES ET DEPENSES_________ POUR LES SUPPRIMER ________________________________________________________
    path('get_all_transactions/', get_all_transactions, name='get_all_transactions'),
    path('delete_transaction/<int:transaction_id>/<str:transaction_type>/', delete_transaction, name='delete_transaction'),

    # AFFICHER LE TABLEAU DE BORD______________________________________________________________
    path('monthly-summary/', monthly_summary, name='monthly_summary'),

    path('subscription/<int:pk>/', AbonnementDetailView.as_view(), name='subscription'),

    # AFFICHER LA PAGE DE PRESENTATION______________________________________________________________
    path('presentation/', PresentationAPIView.as_view(), name='presentation'),

    # AFFICHER LE MONTANT ABONNEMENT LORS INSCRIPTION______________________________________________________________
    path('config-abonnement/', config_abonnement, name='config_abonnement'),

    # AFFICHER LE MONTANT ABONNEMENT LORS INSCRIPTION______________________________________________________________
    path('api/upload_image/', upload_image, name='upload_image'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)