# coding: utf-8
"""
ShaarPy :: Views Links
"""

import logging
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from simple_search import search_form_factory

from shaarpy.forms import LinksForm
from shaarpy.models import Links
from shaarpy.tools import small_hash, url_cleaning
from shaarpy.views import SettingsMixin, SuccessMixin

logger = logging.getLogger("shaarpy.views")


class LinksList(SettingsMixin, ListView):
    """
    home page
    """

    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Links.objects.all()
        else:
            queryset = Links.objects.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)

        SearchForm = search_form_factory(queryset, ["^title", "text", "tags"])

        search_form = SearchForm(self.request.GET or {})
        if self.request.GET.get("q"):
            if search_form.is_valid():
                queryset = search_form.get_queryset()

        context = super(LinksList, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context["paginator"] = paginator
        context["page_obj"] = page
        context["is_paginated"] = is_paginated
        context["object_list"] = queryset
        context["form_search"] = SearchForm
        context["q"] = self.request.GET.get("q")
        # this will be used for the URL in the bookmarklet
        context["hostname"] = self.request.build_absolute_uri()

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class LinksCreate(LoginRequiredMixin, SuccessMixin, SettingsMixin, CreateView):
    """
    add a link / note
    """

    model = Links
    form_class = LinksForm

    # to deal with the popup form trigger from a javascript bookmarklet
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        if self.object:
            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context["add_link"] = True
        context.update(kwargs)
        return super().get_context_data(**context)

    # to deal with the popup form trigger from a javascript bookmarklet

    def get_initial(self) -> dict[str, Any]:
        initial = {}
        if self.request.GET.get("post"):
            url = self.request.GET.get("post")
            url = url_cleaning(str(url))
            initial = {"url": url, "title": self.request.GET.get("title")}
        return initial

    def form_valid(self, form):
        url = form.cleaned_data["url"]
        url = url_cleaning(url)
        if url:
            try:
                # check if url already exist and then redirect to it
                links = Links.objects.get(url=url)
                msg = f"ShaarPy :: link already exists {url}"
                logger.debug(msg)
                return redirect("link_detail", **{"slug": links.url_hashed})
            except Links.DoesNotExist:
                pass

        else:
            self.object = form.save()
            if self.object.title is None:
                self.object.title = "Note:"

        self.object = form.save()

        # generate the tiny url
        self.object.url_hashed = small_hash(self.object.date_created.strftime("%Y%m%d_%H%M%S"))

        self.object = form.save()

        # to deal with the popup form trigger from a javascript bookmarklet
        if self.request.GET.get("source") == "bookmarklet":
            return HttpResponse('<script type="text/javascript">window.close();</script>')

        return super().form_valid(form)


class LinksUpdate(LoginRequiredMixin, SuccessMixin, SettingsMixin, UpdateView):
    """
    update a link / note
    """

    model = Links
    form_class = LinksForm
    slug_field = "url_hashed"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        if self.object:
            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context["edit_link"] = True
        context.update(kwargs)
        return super().get_context_data(**context)


class LinksDelete(LoginRequiredMixin, SettingsMixin, DeleteView):
    """
    delete a link / note
    """

    model = Links
    success_url = reverse_lazy("home")


class LinksDetail(SettingsMixin, DetailView):
    """
    view a link / note
    """

    model = Links
    slug_field = "url_hashed"
