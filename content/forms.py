from constance import config
from django import forms
from django.forms import ModelForm

from .models import Team, Post

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
            'phone',
            'address'
        )
        labels = {
            'active': '',
            'wait': '',
            'date': '',
            'name': '',
            'company': '',
            'contact': '',
            'email': '',
            'phone': '',
            'address':''
        }
        widgets = {
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': config.placeholderTeamActive
                }
            ),
            'wait': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': config.placeholderTeamWaitlist
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamSignupDate,
                    'type': 'date'
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamName
                }
            ),
            'company': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamCompany
                }
            ),
            'contact': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamCaptain
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamEmail
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamPhone
                }
            )
            ,
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamAddress
                }
            )
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = (
            'enable',
            'site',
            'content'
        )

        labels = {
            'enable': '',
            'site': '',
            'content': ''
        }

        widgets = {
            'enable': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input m-0'
                }
            ),
            'site': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': config.placeholderPostContent
                }
            )
        }