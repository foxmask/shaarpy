# coding: utf-8
"""
ShaarPy :: Views Tags
"""

import logging

from django.views.generic import ListView

from shaarpy.models import Links
from shaarpy.views import SettingsMixin

logger = logging.getLogger("shaarpy.views")


class LinksByTagList(SettingsMixin, ListView):
    """
    LinksByTag List
    """

    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        """
        get the links with that tags
        """
        tags = None if self.kwargs["tags"] == "0Tag" else self.kwargs["tags"]
        # when tags is None
        # get the data with tags is null
        if tags:
            queryset = Links.objects.filter(tags__contains=tags)
        else:
            queryset = Links.objects.filter(tags__exact=None)

        # to not return private links, reduce the queryset to public links only
        if self.request.user.is_authenticated is False:
            queryset = queryset.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LinksByTagList, self).get_context_data(**kwargs)
        context["tag"] = self.kwargs["tags"]
        context.update(kwargs)
        return super().get_context_data(**context)


class TagsList(SettingsMixin, ListView):
    """
    Tags List
    """

    template_name = "shaarpy/tags_list.html"
    queryset = Links.objects.none()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Links.objects.all()
        else:
            queryset = Links.objects.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)
        tags = []
        for data in queryset:
            if data.tags is not None:
                for tag in data.tags.split(","):
                    tags.append(tag)
            else:
                tags.append("0Tag")
        tags = sorted(tags)
        tags_dict = {}
        for my_tag in tags:
            tags_dict.update({my_tag: tags.count(my_tag)})

        context = {"object_list": queryset, "tags": tags_dict}

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)
