import string

from constance import config
from django import forms
from django.forms import ModelForm

from .models import Team, Post, Skipper, Training, Category

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = (
            'active',
            'wait',
            'position',
            'date',
            'name',
            'nofee',
            'company',
            'category_id',
            'contact',
            'email',
            'phone',
            'address'
        )
        labels = {
            'active': '',
            'wait': '',
            'position': '',
            'date': '',
            'name': '',
            'nofee': '',
            'company': '',
            'category_id': '',
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
            'position': forms.NumberInput(
                attrs = {
                    'class': 'form-control text-end pe-4',
                    'placeholder': config.placeholderTeamPosition,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamPosition,
                    'inc': 1,
                    'type': 'number'
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control text-end px-1',
                    'placeholder': config.placeholderTeamSignupDate,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamSignupDate,
                    'type': 'date'
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamName,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamName
                }
            ),
            'nofee': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': config.placeholderTeamNoFee
                }
            ),
            'company': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamCompany,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamCompany
                }
            ),
            'category_id': forms.NumberInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderCategoryName,
                    'icon': 'grid'
                }
            ),
            'contact': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamCaptain,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamCaptain
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamEmail,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamEmail
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamPhone,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamPhone
                }
            )
            ,
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': config.placeholderTeamAddress,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTeamAddress
                }
            )
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
            'tag',
        )
        labels = {
            'name': '',
            'tag': '',
        }
        widgets = {
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderCategoryName,
                    'data-bs-tooltip': '',
                    'title': config.placeholderCategoryName,
                },
            ),
            'tag': forms.Select(
                attrs = {
                    'class': 'form-select',
                    'placeholder': config.placeholderCategoryTag,
                    'data-bs-tooltip': '',
                    'title': config.placeholderCategoryTag,
                    'choices': list(string.ascii_uppercase),
                },
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
                    'placeholder': config.placeholderPostContent,
                    'data-bs-tooltip': '',
                    'title': config.placeholderPostContent
                }
            )
        }

class SkipperForm(forms.ModelForm):
    class Meta:
        model = Skipper

        fields = (
            'name',
            'active',
            'fname',
            'lname',
            'email'
        )

        labels = {
            'name': '',
            'active': '',
            'fname': '',
            'lname': '',
            'email': ''
        }

        widgets = {
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperName,
                    'data-bs-tooltip': '',
                    'title': config.placeholderSkipperName
                }
            ),
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input m-0',
                    'placeholder': config.placeholderSkipperActive,
                    'data-bs-tooltip': '',
                    'title': config.placeholderSkipperActive
                }
            ),
            'fname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperFName,
                    'data-bs-tooltip': '',
                    'title': config.placeholderSkipperFName
                }
            ),
            'lname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperLName,
                    'data-bs-tooltip': '',
                    'title': config.placeholderSkipperLName
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.placeholderSkipperEmail,
                    'data-bs-tooltip': '',
                    'title': config.placeholderSkipperEmail
                }
            )
        }

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training

        fields = (
            'active',
            'date',
            'time',
            'duration',
            'skipper_id',
            'team_id',
            'notes'
        )

        labels = {
            'active': '',
            'date': '',
            'time': '',
            'duration': '',
            'skipper_id': '',
            'team_id': '',
            'notes': ''
        }

        widgets = {
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input',
                    'placeholder': config.placeholderTrainingActive
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control text-end px-1',
                    'placeholder': config.placeholderTrainingDateTime,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTrainingDateTime,
                    'type': 'date',
                    'icon': 'calendar-event'
                }
            ),
            'time': forms.TimeInput(
                format=('%H:%M'),
                attrs = {
                    'class': 'form-control text-end rounded-end px-1',
                    'placeholder': config.placeholderTrainingDateTime,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTrainingDateTime,
                    'type': 'time',
                    'list': 'training_time_select',
                    'icon': 'clock'
                }
            ),
            'duration': forms.TimeInput(
                format=('%H:%M'),
                attrs={
                    'class': 'form-control',
                    'placeholder': config.intervalTrainingLengthLabel,
                    'data-bs-tooltip': '',
                    'title': config.intervalTrainingLengthLabel,
                    'icon': 'clock-history',
                    'class': 'form-control text-end px-1',
                    'type': 'time'
                }
            ),
            'skipper_id': forms.NumberInput(
                attrs = {
                    'class': 'form-control',
                    'placeholder': config.skipper,
                    'icon': 'person'
                }
            ),
            'team_id': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': config.placeholderTeamName,
                    'icon': 'tag'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': config.placeholderTrainingNotes,
                    'data-bs-tooltip': '',
                    'title': config.placeholderTrainingNotes,
                    'icon': 'house'
                }
            )
        }