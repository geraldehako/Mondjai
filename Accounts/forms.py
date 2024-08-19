# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Utilisateurs

# BACK OFFICE_____________________________________________________________________________________________________________________________________________
class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateurs
        fields = [
            'first_name', 'last_name', 'username', 'email',  
            'sexe', 'matrimoniale', 'nombre_enfant', 'profession', 'telephone', 
            'photo'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'identifiant'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'adresse e-mail'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'matrimoniale': forms.Select(attrs={'class': 'form-select'}),
            'nombre_enfant': forms.NumberInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez la profession'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le numéro de téléphone'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class UtilisateurmForm(forms.ModelForm):
    class Meta:
        model = Utilisateurs
        fields = [
            'first_name', 'last_name', 'email',  
            'sexe', 'matrimoniale', 'nombre_enfant', 'profession', 'telephone', 
            'photo'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'adresse e-mail'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'matrimoniale': forms.Select(attrs={'class': 'form-select'}),
            'nombre_enfant': forms.NumberInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez la profession'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le numéro de téléphone'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
# _____________________________________________________________________________________________________________________________________________


# _____________________________________________________________ MOBILE ________________________________________________________________________________
class UtilisateursCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateurs
        fields = ('username', 'first_name', 'last_name', 'email', 'photo', 'role', 'statut', 'sexe', 'matrimoniale', 'nombre_enfant')

class UtilisateursChangeForm(UserChangeForm):
    class Meta:
        model = Utilisateurs
        fields = ('username', 'first_name', 'last_name', 'email', 'photo', 'role', 'statut', 'sexe', 'matrimoniale', 'nombre_enfant')


# _____________________________________________________________________________________________________________________________________________
class UsernameChangeForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez un nouveau nom d’utilisateur',
                'aria-label': 'Nom d’utilisateur',
            }
        ),
        label='Nom d’utilisateur',
        help_text='Requis. 150 caractères ou moins.',
        error_messages={
            'required': 'Ce champ est requis.',
            'max_length': 'Le nom d’utilisateur ne peut pas dépasser 150 caractères.',
        }
    )

    class Meta:
        model = Utilisateurs
        fields = ['username']

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères, ne doit pas être entièrement numérique, et ne doit pas être trop similaire à vos autres informations personnelles."),
        min_length=8,
        error_messages={
            'min_length': _('Le mot de passe doit contenir au moins 8 caractères.'),
        }
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Entrez à nouveau votre nouveau mot de passe pour confirmation."),
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        
        return new_password2

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user

# _____________________________________________________________________________________________________________________________________________