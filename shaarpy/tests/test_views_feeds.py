# coding: utf-8
"""
ShaarPy :: Test Feeds rendering
"""

from django.test import RequestFactory, TestCase

from shaarpy.models import Links
from shaarpy.views.feeds import LatestLinksFeed


class LatestLinksFeedTestCase(TestCase):
    """
    test Feed
    """

    def create_links(self):
        """
        fixture
        """
        url = "https://foxmask.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        tags = "home,sweet,"
        return Links.objects.create(
            url=url, title=title, text=text, private=private, sticky=sticky, tags=tags
        )

    def test_linksfeed(self):
        """
        lets test the link feed
        """
        # Setup request and view.
        self.create_links()
        request = RequestFactory().get("feed")
        view = LatestLinksFeed()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
