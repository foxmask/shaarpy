# coding: utf-8
"""
    ShaarPy Test Sitemap
"""

from django.test import RequestFactory, TestCase
from django.contrib.sitemaps.views import sitemap
from shaarpy.sitemaps import ShaarpySitemap


class ShaarpySitemapTestCase(TestCase):
    """
    Test sitemap
    """

    def test_sitemaps(self):
        """
        test to check the sitemap
        """

        request = RequestFactory().get('sitemap.xml')
        kw = {'sitemaps': {'shaarpy': ShaarpySitemap}}
        response = sitemap(request, **kw)
        response['Headers'] = 'Last-Modified'
        # Check.
        self.assertEqual(response.status_code, 200)
       
        # @TODO triggering
        # - lastmod
        # - location
