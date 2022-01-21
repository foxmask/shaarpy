# coding: utf-8
"""
    ShaarPy :: Forms
"""
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, EmailInput

from shaarpy.models import Links
from simple_search import search_form_factory


class LinksForm(ModelForm):

    class Meta:
        model = Links
        fields = ('url', 'title', 'text', 'tags', 'private')
        widgets = {
            'tags': TextInput(attrs={'class': 'form-control'}),
            'url': TextInput(attrs={'class': 'form-control', 'placeholder': _('Drop an URL or leave if empty for creating a note')}),
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': _('Note:')}),
            'text': Textarea(attrs={'class': 'form-control', 'placeholder': _('content')}),
            'private': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")

        if url is None and title is None and text == '':
            msg = "You need to enter something in one of those fields 'URL' or 'Title' or 'Text'"
            self.add_error('url', msg)
            self.add_error('title', msg)
            self.add_error('text', msg)

    def clean_tags(self):
        """
            remove extra space
        """
        data = self.cleaned_data['tags']
        if data:
            if data.endswith(','):
                data = data[:-1]
            return data.replace(' ', '')


# search engine from the nice [simple_search](https://github.com/gregplaysguitar/django-simple-search)
# a search engine like in the admin
SearchForm = search_form_factory(Links.objects.all(), ['^title', 'text', 'tags'])


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
