# forms.py
from django import forms
from .models import Configabonnement,Abonnement,Presentation

class AbonnementForm(forms.ModelForm):
    class Meta:
        model = Abonnement
        fields = [
            'date_debut', 'date_fin'
        ]

        widgets = {
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ConfigAbonForm(forms.ModelForm):
    class Meta:
        model = Configabonnement
        fields = [
            'montant', 'pourcentage'
        ]

        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'pourcentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = [
            'logo', 'contact','presentation_text','welcome_message','video_url','site' ,'email' , 'whatsapp', 'facebook','pub'
        ]

        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control','type':'file'}),
            'contact': forms.TextInput(attrs={'class':'form-control','placeholder': 'Entrez le contact'}),
            'presentation_text': forms.TextInput(attrs={'class':'form-control','placeholder': 'Entrez la presentation'}),
            'welcome_message': forms.TextInput(attrs={'class':'form-control','placeholder': 'Entrez le message de bienvenue'}),
            'video_url': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez l\'URL de la vidéo'}),
            'site': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez l\'URL de la site'}),
            'email': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez l\'URL de la vidéo'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez l\'URL de la vidéo'}),
            'facebook': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez l\'URL de la vidéo'}),
            'pub': forms.FileInput(attrs={'class': 'form-control','type':'file'}),
        }