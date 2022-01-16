# coding: utf-8
"""
   ShaarPy
"""
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, PasswordInput, EmailInput

from shaarpy.models import Links


class LinksForm(ModelForm):

    class Meta:
        model = Links
        fields = ('url', 'title', 'text', 'tags', 'private')
        widgets = {
            'tags': TextInput(attrs={'class': 'form-control'}),
            'url': TextInput(attrs={'class': 'form-control', 'placeholder': _('URL or leave if empty for creating a note')}),
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': _('Note:')}),
            'text': Textarea(attrs={'class': 'form-control', 'placeholder': _('content')}),
            'private': CheckboxInput(attrs={'class': 'form-check-input'}),
        }


#class LoginForm(ModelForm):
#    """
#        Form to manage the login page
#    """
#    class Meta:
#        model = User
#        fields = ('username', 'password')
#        widgets = {
#            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
#            'password': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
#        }


class MeForm(ModelForm):

    """
        form to edit its profile
    """

    class Meta:

        model = User
        fields = ('email', 'last_name')
        widgets = {
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Last name')}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
        }
