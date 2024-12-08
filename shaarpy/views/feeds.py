# coding: utf-8
"""
ShaarPy :: Views Feeds
"""

import logging

import markdown
from django.contrib.syndication.views import Feed
from django.urls import reverse

from shaarpy import settings
from shaarpy.models import Links
from shaarpy.views import SettingsMixin

logger = logging.getLogger("shaarpy.views")


# the feeds
class LatestLinksFeed(SettingsMixin, Feed):
    """
    Generate an RSS Feed
    https://docs.djangoproject.com/en/5.0/ref/contrib/syndication/
    """

    title = settings.SHAARPY_NAME
    link = "/"
    description = settings.SHAARPY_DESCRIPTION

    def items(self):
        return Links.objects.filter(private=False).order_by("-date_created")[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.text)

    def item_link(self, item):
        return reverse("link_detail", args=[item.url_hashed])

    def item_pubdate(self, item):
        return item.date_created
