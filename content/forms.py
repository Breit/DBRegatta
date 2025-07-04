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
                    'class': 'form-check-input'
                }
            ),
            'wait': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input'
                }
            ),
            'position': forms.NumberInput(
                attrs = {
                    'class': 'form-control text-end pe-4',
                    'data-bs-tooltip': '',
                    'inc': 1,
                    'type': 'number'
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control text-end px-1',
                    'data-bs-tooltip': '',
                    'type': 'date'
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            ),
            'nofee': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input'
                }
            ),
            'company': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            ),
            'category_id': forms.NumberInput(
                attrs = {
                    'class': 'form-control',
                    'icon': 'grid'
                }
            ),
            'contact': forms.TextInput(
                attrs = {
                    'class': 'form-control',
                    'data-bs-tooltip': '',
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            )
            ,
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'data-bs-tooltip': ''
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['active'].widget.attrs['placeholder'] = config.placeholderTeamActive
        self.fields['wait'].widget.attrs['placeholder'] = config.placeholderTeamWaitlist
        self.fields['position'].widget.attrs['placeholder'] = config.placeholderTeamPosition
        self.fields['position'].widget.attrs['title'] = config.placeholderTeamPosition
        self.fields['date'].widget.attrs['placeholder'] = config.placeholderTeamSignupDate
        self.fields['date'].widget.attrs['title'] = config.placeholderTeamSignupDate
        self.fields['name'].widget.attrs['placeholder'] = config.placeholderTeamName
        self.fields['name'].widget.attrs['title'] = config.placeholderTeamName
        self.fields['nofee'].widget.attrs['placeholder'] = config.placeholderTeamNoFee
        self.fields['company'].widget.attrs['placeholder'] = config.placeholderTeamCompany
        self.fields['company'].widget.attrs['title'] = config.placeholderTeamCompany
        self.fields['category_id'].widget.attrs['placeholder'] = config.placeholderCategoryName
        self.fields['contact'].widget.attrs['placeholder'] = config.placeholderTeamCaptain
        self.fields['contact'].widget.attrs['title'] = config.placeholderTeamCaptain
        self.fields['email'].widget.attrs['placeholder'] = config.placeholderTeamEmail
        self.fields['email'].widget.attrs['title'] = config.placeholderTeamEmail
        self.fields['phone'].widget.attrs['placeholder'] = config.placeholderTeamPhone
        self.fields['phone'].widget.attrs['title'] = config.placeholderTeamPhone
        self.fields['address'].widget.attrs['placeholder'] = config.placeholderTeamAddress
        self.fields['address'].widget.attrs['title'] = config.placeholderTeamAddress

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
                    'data-bs-tooltip': ''
                },
            ),
            'tag': forms.Select(
                attrs = {
                    'class': 'form-select',
                    'data-bs-tooltip': '',
                    'choices': list(string.ascii_uppercase),
                },
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = config.placeholderCategoryName
        self.fields['name'].widget.attrs['title'] = config.placeholderCategoryName
        self.fields['tag'].widget.attrs['placeholder'] = config.placeholderCategoryTag
        self.fields['tag'].widget.attrs['title'] = config.placeholderCategoryTag

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
                    'data-bs-tooltip': ''
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = config.placeholderPostContent
        self.fields['content'].widget.attrs['title'] = config.placeholderPostContent

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
                    'data-bs-tooltip': ''
                }
            ),
            'active': forms.CheckboxInput(
                attrs = {
                    'class': 'form-check-input m-0',
                    'data-bs-tooltip': ''
                }
            ),
            'fname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            ),
            'lname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class': 'form-control',
                    'data-bs-tooltip': ''
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = config.placeholderSkipperName
        self.fields['name'].widget.attrs['title'] = config.placeholderSkipperName
        self.fields['active'].widget.attrs['placeholder'] = config.placeholderSkipperActive
        self.fields['active'].widget.attrs['title'] = config.placeholderSkipperActive
        self.fields['fname'].widget.attrs['placeholder'] = config.placeholderSkipperFName
        self.fields['fname'].widget.attrs['title'] = config.placeholderSkipperFName
        self.fields['lname'].widget.attrs['placeholder'] = config.placeholderSkipperLName
        self.fields['lname'].widget.attrs['title'] = config.placeholderSkipperLName
        self.fields['email'].widget.attrs['placeholder'] = config.placeholderSkipperEmail
        self.fields['email'].widget.attrs['title'] = config.placeholderSkipperEmail

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
                    'class': 'form-check-input'
                }
            ),
            'date': forms.DateInput(
                attrs = {
                    'class': 'form-control text-end px-1',
                    'data-bs-tooltip': '',
                    'type': 'date',
                    'icon': 'calendar-event'
                }
            ),
            'time': forms.TimeInput(
                format=('%H:%M'),
                attrs = {
                    'class': 'form-control text-end rounded-end px-1',
                    'data-bs-tooltip': '',
                    'type': 'time',
                    'list': 'training_time_select',
                    'icon': 'clock'
                }
            ),
            'duration': forms.TimeInput(
                format=('%H:%M'),
                attrs={
                    'class': 'form-control',
                    'data-bs-tooltip': '',
                    'icon': 'clock-history',
                    'class': 'form-control text-end px-1',
                    'type': 'time'
                }
            ),
            'skipper_id': forms.NumberInput(
                attrs = {
                    'class': 'form-control',
                    'icon': 'person'
                }
            ),
            'team_id': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'icon': 'tag'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'data-bs-tooltip': '',
                    'icon': 'house'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['active'].widget.attrs['placeholder'] = config.placeholderTrainingActive
        self.fields['date'].widget.attrs['placeholder'] = config.placeholderTrainingDateTime
        self.fields['date'].widget.attrs['title'] = config.placeholderTrainingDateTime
        self.fields['time'].widget.attrs['placeholder'] = config.placeholderTrainingDateTime
        self.fields['time'].widget.attrs['title'] = config.placeholderTrainingDateTime
        self.fields['duration'].widget.attrs['placeholder'] = config.intervalTrainingLengthLabel
        self.fields['duration'].widget.attrs['title'] = config.intervalTrainingLengthLabel
        self.fields['skipper_id'].widget.attrs['placeholder'] = config.skipper
        self.fields['team_id'].widget.attrs['placeholder'] = config.placeholderTeamName
        self.fields['notes'].widget.attrs['placeholder'] = config.placeholderTrainingNotes
        self.fields['notes'].widget.attrs['title'] = config.placeholderTrainingNotes