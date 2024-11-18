# coding: utf-8
"""
ShaarPy :: Views Daily
"""

import logging
from datetime import date, datetime, timedelta, timezone

from django.views.generic import ListView

from shaarpy.models import Links
from shaarpy.views import SettingsMixin

logger = logging.getLogger("shaarpy.views")


class DailyLinks(SettingsMixin, ListView):
    """
    Daily Links List
    """

    template_name = "shaarpy/daily_list.html"
    queryset = Links.objects.none()

    def get_queryset(self):
        """
        by default, get the "yesterday" links
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        if "yesterday" in self.kwargs:
            yesterday = self.kwargs["yesterday"]

        # do not return private links
        if self.request.user.is_authenticated is False:
            queryset = Links.objects.filter(date_created__date=yesterday, private=False)
        else:
            queryset = Links.objects.filter(date_created__date=yesterday)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        checkout which "yesterday" it is
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        if "yesterday" in self.kwargs:
            yesterday = self.kwargs["yesterday"]
            yesterday = datetime.strptime(yesterday, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)

        # do not return private links
        if self.request.user.is_authenticated is False:
            previous_date = (
                Links.objects.filter(date_created__lte=yesterday, private=False)
                .order_by("-date_created")
                .first()
            )
        else:
            previous_date = (
                Links.objects.filter(date_created__lte=yesterday).order_by("-date_created").first()
            )

        if previous_date:
            previous_date = previous_date.date_created.date()

        # do not return private links
        if self.request.user.is_authenticated is False:
            next_date = (
                Links.objects.filter(date_created__date__gt=yesterday, private=False)
                .order_by("date_created")
                .first()
            )
        else:
            next_date = (
                Links.objects.filter(date_created__date__gt=yesterday)
                .order_by("date_created")
                .first()
            )
        if next_date:
            next_date = next_date.date_created.date()

        context = {
            "object_list": queryset,
            "previous_date": previous_date,
            "next_date": next_date,
            "current_date": yesterday,
        }

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)
