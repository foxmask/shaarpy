# coding: utf-8
"""
    ShaarPy
"""
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from shaarpy.forms import LinksForm
from shaarpy.views.links import LinksList, LinksCreate, LinksDelete, LinksDetail, LinksUpdate
from shaarpy.tests.test_common import CommonStuffTestCase


class LinksDeleteTestCase(CommonStuffTestCase):
    """
    Deal with deletion
    """

    def test_delete(self):
        link = self.create_link()
        template = "shaarpy/links_confirm_delete.html"
        # Setup request and view.
        request = RequestFactory().get(f'delete/{link.id}')
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
        request = RequestFactory().get('/')
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
        request = RequestFactory().get('/?q=foobar')
        request.user = self.user

        view = LinksList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_close_bookmarklet(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/?source=bookmarklet')
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
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        view = LinksList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


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
        url_to_create = 'https://foxmask.eu.org/feeds/all.atom.xml'
        title = 'Le Free de la passion'
        url_data = f"?post={url_to_create}&title={title}&source=bookmarklet"
        request = RequestFactory().get(reverse('link_create') + url_data)
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
        url_to_create = 'https://foxmask.eu.org/'
        data = {
            'url': url_to_create,
            'title': '',
            'text': '',
            'tags': 'home,sweet,',
        }
        request = RequestFactory().post(reverse('link_create'), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create_link_duplicate(self):
        # check to avoid creating duplicate of the same URL
        data = {
            'url': 'https://foxmask.eu.org/',
            'title': 'Le Free de la passion',
            'text': '# Le Free de la Passion',
            'private': False,
            'sticky': True,
            'tags': 'home,sweet,'
        }
        request = RequestFactory().post(reverse('link_create'), data=data)
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
        title = 'Le Free de la passion'
        text = '# Le Free de la passion'
        data = {
            'url': '',
            'title': title,
            'text': text,
            'tags': 'home,sweet,',
        }
        request = RequestFactory().post(reverse('link_create'), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create_note_wo_title(self):
        text = '# Le Free de la passion'
        data = {
            'url': '',
            'title': '',
            'text': text,
        }
        request = RequestFactory().post(reverse('link_create'), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_create3_drop_image(self):
        # create an entry into the model
        url = 'http://world.kbs.co.kr/service/index.htm?lang=e'
        title = 'KBS World'
        text = '# KBS World'
        private = False
        sticky = True
        tags = 'Korea'
        data = {
            'url': url,
            'title': title,
            'text': text,
            'private': private,
            'sticky': sticky,
            'tags': tags,
        }
        # try to create an entry from the form but with same URL
        request = RequestFactory().post(reverse('link_create'), data=data)
        request.user = self.user
        view = LinksCreate.as_view()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        data = {'url': 'https://foxmask.eu.org/', 'text': '', 'title': '', 'tags': 'home,sweet,'}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_valid_url_cleaning(self):
        data = {'url': 'https://foxmask.eu.org/?utm_source=foo&utm_source=bar', 'tags': 'home,sweet,'}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_valid2(self):
        data = {'title': 'My note', 'text': 'note text'}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_valid3(self):
        data = {'url': '', 'title': '', 'text': 'note text'}
        form = LinksForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        data = {'url': '', 'title': '', 'text': ''}
        form = LinksForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid2(self):
        data = {'title': 'My note', 'text': 'note text', 'tags': '@toto'}
        form = LinksForm(data=data)
        self.assertFalse(form.is_valid())


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
        request = RequestFactory().get(reverse('link_detail', kwargs={'slug': link.url_hashed}))
        view = LinksDetail.as_view(template_name=template)
        # Run.
        response = view(request, pk=link.id)   # @TODO why pk=link.id and not slug=link.url_hashed ?
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
        request = RequestFactory().get(reverse('link_edit', kwargs={'pk': link.id}))
        request.user = self.user
        view = LinksUpdate.as_view(template_name=template)
        # Run.
        response = view(request, pk=link.id)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
