# coding: utf-8
"""
ShaarPy :: Test all Link methods
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from shaarpy.forms import LinksForm
from shaarpy.models import Links
from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.views.links import LinksCreate, LinksDelete, LinksDetail, LinksList, LinksUpdate


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
        request.user = self.user
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


class LinksCreateViewTests(CommonStuffTestCase):
    def setUp(self):
        super(LinksCreateViewTests, self).setUp()
        self.url = reverse("link_create")
        self.factory = RequestFactory()

    def test_get_context_data_with_object(self):
        request = self.factory.get(self.url)
        request.user = self.user
        view = LinksCreate()
        view.setup(request)
        view.object = Links.objects.create(
            url="http://example1.com",
            title="Test Link1",
        )

        context = view.get_context_data()

        self.assertIn("object", context)
        self.assertEqual(context["object"], view.object)
        self.assertIn("add_link", context)
        self.assertTrue(context["add_link"])

    def test_get_context_data_without_object(self):
        request = self.factory.get(self.url)
        request.user = self.user
        view = LinksCreate()
        view.setup(request)
        view.object = None

        context = view.get_context_data()

        self.assertNotIn("object", context)
        self.assertIn("add_link", context)
        self.assertTrue(context["add_link"])

    def test_get_initial_with_get_parameters(self):
        request = self.factory.get(
            self.url, data={"post": "http://example2.com", "title": "Test Title2"}
        )
        request.user = self.user
        view = LinksCreate()
        view.setup(request)

        initial = view.get_initial()

        self.assertIn("url", initial)
        self.assertEqual(initial["url"], "http://example2.com")
        self.assertIn("title", initial)
        self.assertEqual(initial["title"], "Test Title2")

    def test_get_initial_without_get_parameters(self):
        request = self.factory.get(self.url)
        request.user = self.user
        view = LinksCreate()
        view.setup(request)

        initial = view.get_initial()
        self.assertEqual(initial, {})

    def test_form_valid_with_existing_url(self):
        existing_link = Links.objects.create(
            url="http://example4.com",
            title="Existing Link",
        )
        request = self.factory.post(
            self.url, data={"url": "http://example4.com", "title": "New Title4"}
        )
        request.user = self.user
        view = LinksCreate()
        view.setup(request)
        form = LinksForm(data={"url": "http://example4.com", "title": "New Title4"})
        form.is_valid()

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("link_detail", kwargs={"slug": existing_link.url_hashed})
        )

    def test_form_valid_with_new_url(self):
        data = {"url": "http://newsite.com", "title": "New Website"}
        request = self.factory.post(self.url, data=data)
        request.user = self.user
        view = LinksCreate()
        view.setup(request)
        form = LinksForm(data=data)
        form.is_valid()

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Links.objects.filter(url="http://newsite.com").exists())

    def test_form_valid_with_bookmarklet(self):

        data = {
            "url": "http://newsite2.com",
            "title": "New Website2",
        }

        url_to_create = "https://foxmask.eu.org/feeds/all.atom.xml"
        title = "Le Free de la passion"
        url_data = f"?post={url_to_create}&title={title}&source=bookmarklet"

        request = self.factory.get(reverse("link_create") + url_data)
        # original request = self.factory.get(self.url, data=data)

        request.user = self.user
        # view = LinksCreate.as_view(template_name=template)

        view = LinksCreate()
        view.setup(request)
        form = LinksForm(data=data)
        form.is_valid()

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 200)
