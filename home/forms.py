from django import forms
from django.forms import ModelForm

from .models import Team

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = (
            # 'active',
            'name',
            'company',
            'contact',
            'email',
            'address'
        )
        labels = {
            # 'active': '',
            'name': '',
            'company': '',
            'contact': '',
            'email': '',
            'address': ''
        }
        widgets = {
            # 'active': forms.CheckboxInput(
            #     attrs = {
            #         'class': 'form_control_check'
            #     }
            # ),
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
            'address': forms.TextInput(
                attrs={
                    'class': 'form_control',
                    'placeholder': 'Anschrift'
                }
            )
        }
