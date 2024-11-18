# coding: utf-8
"""
ShaarPy :: Test Public/Private Links
"""

from django.test import RequestFactory

from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.views.pub_priv_links import PrivateLinks, PublicLinks


class PrivateLinksTestCase(CommonStuffTestCase):
    """
    Private Links for the current user
    """

    def test_private_links_list(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get("/links/private/")
        request.user = self.user

        view = PrivateLinks.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class PublicLinksTestCase(CommonStuffTestCase):
    """
    Public Links for the current user
    """

    def test_public_links_list(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get("/links/public/")
        request.user = self.user

        view = PublicLinks.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
