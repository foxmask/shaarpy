# coding: utf-8
"""
ShaarPy :: Test Public/Private Links
"""

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.views.pub_priv_links import PrivateLinks, PublicLinks


class PrivateLinksTestCase(CommonStuffTestCase):
    """
    Private Links for the current user
    """

    def setUp(self):
        super(PrivateLinksTestCase, self).setUp()

    def test_private_links_list_without_permission(self):
        self.create_link()
        template = "shaarpy/links_list.html"

        request = RequestFactory().get("/links/private/")
        request.user = self.user_no_perm

        view = PrivateLinks.as_view(template_name=template)

        with self.assertRaises(PermissionDenied):
            response = view(request)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.status_code, 403)

    def test_private_links_list_with_permission(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        request = RequestFactory().get("/links/private/")
        request.user = self.user

        view = PrivateLinks.as_view(template_name=template)
        response = view(request)

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
