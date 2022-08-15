from django import forms
from django.forms import ModelForm

from .models import Team

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = (
            'active',
            'wait',
            'name',
            'company',
            'contact',
            'email',
            'phone',
            'date'
        )
        labels = {
            'active': '',
            'wait': '',
            'name': '',
            'company': '',
            'contact': '',
            'email': '',
            'phone': '',
            'date': ''
        }
        widgets = {
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': 'Team aktiv'
                }
            ),
            'wait': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': 'Warteliste'
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': 'Teamname'
                }
            ),
            'company': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': 'Firma'
                }
            ),
            'contact': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': 'Kontakt / Team Captain'
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': 'Email Adresse'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Telefonnummer'
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': 'Anmeldedatum',
                    'type': 'date'
                }
            )
        }
