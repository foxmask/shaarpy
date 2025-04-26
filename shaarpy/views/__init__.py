# coding: utf-8
"""
ShaarPy :: Views
"""

from typing import Any

from django.urls import reverse

from shaarpy import settings


class SuccessMixin(object):
    """
    back to detail
    """

    def get_success_url(self) -> str:
        """
        redirect to the Detail object page
        """
        return reverse("link_detail", kwargs={"slug": self.object.url_hashed})  # type: ignore


class SettingsMixin(object):
    """
    mixin to add settings related app data to the templates
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        return settings
        """
        context = super(SettingsMixin, self).get_context_data(**kwargs)
        context["SHAARPY_NAME"] = settings.SHAARPY_NAME
        context["SHAARPY_DESCRIPTION"] = settings.SHAARPY_DESCRIPTION
        context["SHAARPY_AUTHOR"] = settings.SHAARPY_AUTHOR
        context["SHAARPY_ROBOT"] = settings.SHAARPY_ROBOT

        return context
