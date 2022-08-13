from django import forms
from django.forms import ModelForm

from .models import Team

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = (
            'active',
            'wait',
            'date',
            'name',
            'company',
            'contact',
            'email',
            'phone'
        )
        labels = {
            'active': '',
            'wait': '',
            'date': '',
            'name': '',
            'company': '',
            'contact': '',
            'email': '',
            'phone': ''
        }
        widgets = {
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form_control_check',
                    'placeholder': 'Team aktiv'
                }
            ),
            'wait': forms.CheckboxInput(
                attrs = {
                    'class': 'form_control_check',
                    'placeholder': 'Warteliste'
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form_control_check',
                    'placeholder': 'Anmeldung'
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'class': 'form_control',
                    'placeholder': 'Teamname'
                }
            ),
            'company': forms.TextInput(
                attrs = {
                    'class': 'form_control',
                    'placeholder': 'Firma'
                }
            ),
            'contact': forms.TextInput(
                attrs = {
                    'class': 'form_control',
                    'placeholder': 'Kontakt / Team Captain'
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form_control',
                    'placeholder': 'Email Adresse'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form_control',
                    'placeholder': 'Telefonnummer'
                }
            )
        }
