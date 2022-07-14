# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shaarpy.models import Links


class ShaarpySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Links.objects.filter(private=False).order_by('-date_created')[:15]

    def lastmod(self, obj):
        return obj.date_created

    def location(self, item):
        return reverse('link_detail', kwargs={'slug': item.url_hashed})
