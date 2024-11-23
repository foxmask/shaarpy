# coding: utf-8
"""
ShaarPy :: Test Tags rendering / Accessing
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from shaarpy.models import Links
from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.views.tags import LinksByTagList, TagsList


class LinksByTagListTestCase(CommonStuffTestCase):
    """
    Deal with displaying Links for a given tag
    """

    def test_one_tag(self):
        self.create_link()
        template = "links_list.html"
        # Setup request and view.
        tags = "foobar"

        request = RequestFactory().get(reverse("links_by_tag_list", kwargs={"tags": tags}))
        request.user = self.user

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_no_tag(self):
        self.create_link()

        template = "links_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("links_by_tag_list", kwargs={"tags": "0Tag"}))
        tags = "0Tag"
        request.user = self.user
        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_public_links_from_anonym(self):
        # user object AnonymousUser + private = False
        self.create_link()
        template = "links_list.html"
        # Setup request and view.
        tags = "home"

        request = RequestFactory().get(reverse("links_by_tag_list", kwargs={"tags": tags}))
        request.user = AnonymousUser()

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_public_links_from_auth_user(self):
        # user object User + private = False
        self.create_link()
        template = "links_list.html"
        # Setup request and view.
        tags = "home"

        request = RequestFactory().get(reverse("links_by_tag_list", kwargs={"tags": tags}))
        request.user = self.user

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class TagsListTestCase(CommonStuffTestCase):
    """
    display the list of tags
    """

    def setUp(self):
        super(TagsListTestCase, self).setUp()
        self.factory = RequestFactory()

    def create_links_no_tags(self):
        url = "https://foxmask.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky)

    def test_tag_index_from_auth_user(self):
        self.create_link()
        self.create_links_no_tags()
        template = "tags_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("tags_list"))
        request.user = self.user
        view = TagsList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_tag_index_from_anonym(self):
        self.create_link()
        self.create_links_no_tags()
        template = "tags_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("tags_list"))
        request.user = AnonymousUser()
        view = TagsList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
