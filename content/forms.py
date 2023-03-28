from constance import config
from django import forms
from django.forms import ModelForm

from .models import Team, Post, Skipper, Training

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
                    'class': 'form-control text-end px-1',
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
                    'rows': 4,
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
                    'rows': 12,
                    'placeholder': config.placeholderPostContent
                }
            )
        }

class SkipperForm(forms.ModelForm):
    class Meta:
        model = Skipper

        fields = (
            'name',
            'fname',
            'lname',
            'email',
            'active'
        )

        labels = {
            'name': '',
            'fname': '',
            'lname': '',
            'email': '',
            'active': ''
        }

        widgets = {
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperName
                }
            ),
            'fname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperFName
                }
            ),
            'lname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperLName
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperEmail
                }
            ),
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input m-0',
                    'placeholder': config.placeholderSkipperActive
                }
            )
        }

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training

        fields = (
            'date',
            'time',
            'team_id',
            'skipper_id',
            'notes'
        )

        labels = {
            'date': '',
            'time': '',
            'team_id': '',
            'skipper_id': '',
            'notes': ''
        }

        widgets = {
            'date': forms.DateInput(   # SplitDateTimeWidget?
                attrs = {
                    'class': 'form-control text-end px-1',
                    'placeholder': config.placeholderTrainingDate,
                    'type': 'date'
                }
            ),
            'time': forms.TimeInput(
                attrs={
                    'class': 'form-control text-end px-1',
                    'placeholder': config.placeholderTrainingTime,
                    'type': 'time'
                }
            ),
            'team_id': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamName
                }
            ),
            'skipper_id': forms.Select(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperName
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 12,
                    'placeholder': config.placeholderTrainingNotes
                }
            )
        }