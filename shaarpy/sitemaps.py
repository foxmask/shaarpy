# coding: utf-8
"""
    Sitemap - https://docs.djangoproject.com/en/4.2/ref/contrib/sitemaps/
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shaarpy.models import Links


class ShaarpySitemap(Sitemap):
    """
    Sitemap Shaarpy sauce
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Links.objects.filter(private=False).order_by('-date_created')[:15]

    def lastmod(self, obj):
        """
        obj: object of the sitemap
        """
        return obj.date_created

    def location(self, item):
        return reverse('link_detail', kwargs={'slug': item.url_hashed})
