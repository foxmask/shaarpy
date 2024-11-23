# coding: utf-8
"""
ShaarPy :: Test all Link methods
"""

from django.test import RequestFactory
from django.urls import reverse

from shaarpy.forms import LinksForm
from shaarpy.tests.test_common import CommonStuffTestCase
from shaarpy.tools import is_valid_date, url_cleaning
from shaarpy.views.links import LinksCreate


class LinksCreateTestCase(CommonStuffTestCase):
    """
    Create Links from the form
    """

    def setUp(self):
        super(LinksCreateTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_get_the_form(self):
        template = "link_form.html"
        # Setup request and view.
        url_to_create = "https://foxmask.eu.org/feeds/all.atom.xml"
        title = "Le Free de la passion"
        url_data = f"?post={url_to_create}&title={title}&source=bookmarklet"
        request = RequestFactory().get(reverse("link_create") + url_data)
        request.user = self.user
        view = LinksCreate.as_view(template_name=template)
        # Run.

        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_create_link_alone(self):
        """
        a link alone contains just an URL before the submittion of the form
        then the content of that URL is grabbed
        """
        url_to_create = "https://fr.wiktionary.org/wiki/turlututu"
        data = {
            "url": url_to_create,
            "title": "",
            "text": "",
            "tags": "home,sweet,",
        }
        request = RequestFactory().post(reverse("link_create"), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create_link_duplicate(self):
        # check to avoid creating duplicate of the same URL
        data = {
            "url": "https://foxmask.eu.org/",
            "title": "Le Free de la passion",
            "text": "# Le Free de la Passion",
            "private": False,
            "sticky": True,
            "tags": "home,sweet,",
        }
        request = RequestFactory().post(reverse("link_create"), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create_note(self):
        """
        a note is a Link object without URL
        """
        title = "Le Free de la passion"
        text = "# Le Free de la passion"
        data = {
            "url": "",
            "title": title,
            "text": text,
            "tags": "home,sweet,",
        }
        request = RequestFactory().post(reverse("link_create"), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create_note_wo_title(self):
        text = "# Le Free de la passion"
        title = ""
        data = {
            "url": "",
            "title": title,
            "text": text,
        }
        request = RequestFactory().post(reverse("link_create"), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create3_drop_image(self):
        # create an entry into the model
        url = "http://world.kbs.co.kr/service/index.htm?lang=e"
        title = "KBS World"
        text = "# KBS World"
        private = False
        sticky = True
        tags = "Korea"
        data = {
            "url": url,
            "title": title,
            "text": text,
            "private": private,
            "sticky": sticky,
            "tags": tags,
        }
        # try to create an entry from the form but with same URL
        request = RequestFactory().post(reverse("link_create"), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)

        # Check.
        self.assertEqual(response.status_code, 302)

    def test_form_valid_url_alone(self):
        data = {"url": "https://foxmask.eu.org/", "text": "", "title": "", "tags": "home,sweet,"}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_valid_url_cleaning(self):
        data = {
            "url": "https://foxmask.eu.org/?utm_source=foo&utm_source=bar",
            "tags": "home,sweet,",
        }
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_is_not_valid_date(self):
        date_created = "2020-01-01 99:99:99"
        self.assertFalse(is_valid_date(date_created, "%Y-%m-%d %H:%M:%S"))

    def test_is_valid_date(self):
        date_created = "2020-01-01 00:00:00"
        self.assertTrue(is_valid_date(date_created, "%Y-%m-%d %H:%M:%S"))

    def test_url_cleaning(self):
        url_should_be = "https://foxmask.eu.org/"

        for trash in ("&utm_source=", "?utm_source=", "&utm_medium=", "#xtor=RSS-"):
            url_before = f"https://foxmask.eu.org/{trash}"

            url = url_cleaning(url_before)
            self.assertEqual(url, url_should_be)

    def test_form_valid_wo_url(self):
        data = {"title": "My note", "text": "note text"}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_valid_text_alone(self):
        data = {"url": "", "title": "", "text": "note text"}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_all_empty(self):
        data = {"url": "", "title": "", "text": ""}
        form = LinksForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_tags(self):
        data = {"title": "My note", "text": "note text", "tags": "@toto"}
        form = LinksForm(data=data)
        self.assertFalse(form.is_valid())
