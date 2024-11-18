# coding: utf-8
"""
ShaarPy :: Views Public/Private Links
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from shaarpy.models import Links
from shaarpy.views import SettingsMixin

logger = logging.getLogger("shaarpy.views")


class PublicLinks(SettingsMixin, ListView):
    """
    Public Links List
    """

    def get_queryset(self):
        return Links.objects.filter(private=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        context = super(PublicLinks, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size or 1)
        context["paginator"] = paginator
        context["page_obj"] = page
        context["is_paginated"] = is_paginated
        context["object_list"] = queryset
        context["audience"] = "public"

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class PrivateLinks(LoginRequiredMixin, SettingsMixin, ListView):
    """
    Private Links List
    """

    def get_queryset(self):
        return Links.objects.filter(private=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        context = super(PrivateLinks, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size or 1)
        context["paginator"] = paginator
        context["page_obj"] = page
        context["is_paginated"] = is_paginated
        context["object_list"] = queryset
        context["audience"] = "private"

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context
