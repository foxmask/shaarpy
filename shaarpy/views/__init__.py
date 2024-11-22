# coding: utf-8
"""
ShaarPy :: Views
"""

from typing import Any

from django.http import HttpResponse
from django.shortcuts import render
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


def error_403(request: Any, exception: Any) -> HttpResponse:
    data = {
        "SHAARPY_AUTHOR": settings.SHAARPY_AUTHOR,
        "SHAARPY_NAME": settings.SHAARPY_NAME,
        "SHAARPY_DESCRIPTION": settings.SHAARPY_DESCRIPTION,
        "SHAARPY_ROBOT": settings.SHAARPY_ROBOT,
        "exception": exception,
    }

    return render(request, "shaarpy/403.html", data)


def error_404(request: Any, exception: Any) -> HttpResponse:
    data = {
        "SHAARPY_AUTHOR": settings.SHAARPY_AUTHOR,
        "SHAARPY_NAME": settings.SHAARPY_NAME,
        "SHAARPY_DESCRIPTION": settings.SHAARPY_DESCRIPTION,
        "SHAARPY_ROBOT": settings.SHAARPY_ROBOT,
        "exception": exception,
    }
    return render(request, "shaarpy/404.html", data)


def error_500(request: Any) -> HttpResponse:
    data = {
        "SHAARPY_AUTHOR": settings.SHAARPY_AUTHOR,
        "SHAARPY_NAME": settings.SHAARPY_NAME,
        "SHAARPY_DESCRIPTION": settings.SHAARPY_DESCRIPTION,
        "SHAARPY_ROBOT": settings.SHAARPY_ROBOT,
    }
    return render(request, "shaarpy/500.html", data)
