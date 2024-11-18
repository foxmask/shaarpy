# coding: utf-8
"""
ShaarPy :: Views Me
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView

from shaarpy.forms import MeForm
from shaarpy.views import SettingsMixin

logger = logging.getLogger("shaarpy.views")


class Me(SettingsMixin, LoginRequiredMixin, TemplateView):
    """
    access to the profile page
    """

    template_name = "me.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.request.user
        return context


class MeUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    """
    Update the User profile
    """

    model = User
    form_class = MeForm
    template_name = "edit_me.html"
    success_url = reverse_lazy("me")

    def get_object(self, queryset=None):
        """
        get only the data of the current user
        :param queryset:
        :return:
        """
        return User.objects.get(id=self.request.user.id)
