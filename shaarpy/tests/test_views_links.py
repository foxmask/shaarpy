# coding: utf-8
"""
ShaarPy :: Test all Link methods
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.views.links import LinksDelete, LinksDetail, LinksList, LinksUpdate


class LinksDeleteTestCase(CommonStuffTestCase):
    """
    Deal with deletion
    """

    def test_delete(self):
        link = self.create_link()
        template = "shaarpy/links_confirm_delete.html"
        # Setup request and view.
        request = RequestFactory().get(f"delete/{link.id}")
        request.user = self.user

        view = LinksDelete.as_view(template_name=template)
        # Run.
        response = view(request, user=request.user, pk=link.id)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class LinksListTestCase(CommonStuffTestCase):
    """
    Home View for the current user
    """

    def test_all_links_list(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get("/")
        request.user = self.user

        view = LinksList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_search(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get("/?q=foobar")
        request.user = self.user

        view = LinksList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class LinksListAnonymousTestCase(CommonStuffTestCase):
    """
    Home View for anonymous user
    """

    def setUp(self):
        super(LinksListAnonymousTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_all_links_list(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get("/")
        request.user = AnonymousUser()

        view = LinksList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class LinksDetailTestCase(CommonStuffTestCase):
    """
    Deal with Links detail page
    """

    def setUp(self):
        super(LinksDetailTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_link_detail(self):
        link = self.create_link()
        template = "shaarpy/links_detail.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("link_detail", kwargs={"slug": link.url_hashed}))
        view = LinksDetail.as_view(template_name=template)
        # Run.
        response = view(request, pk=link.id)  # @TODO why pk=link.id and not slug=link.url_hashed ?
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class LinksUpdateTestCase(CommonStuffTestCase):
    """
    Deal with Link updating
    """

    def setUp(self):
        super(LinksUpdateTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_link_update(self):
        link = self.create_link()
        template = "shaarpy/links_form.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("link_edit", kwargs={"pk": link.id}))
        request.user = self.user
        view = LinksUpdate.as_view(template_name=template)
        # Run.
        response = view(request, pk=link.id)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
