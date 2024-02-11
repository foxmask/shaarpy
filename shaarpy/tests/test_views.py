# coding: utf-8
"""
    ShaarPy
"""
from datetime import date, timedelta, datetime, timezone

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from django.urls import reverse

from shaarpy.forms import LinksForm
from shaarpy.models import Links
from shaarpy.views import LinksList, LinksCreate, LinksDelete, LinksDetail, LinksUpdate
from shaarpy.views import DailyLinks, TagsList, LinksByTagList, PrivateLinks, PublicLinks


class CommonStuffTestCase(TestCase):
    """
    Common fixtures
    """

    def create_link(self):
        """
        create a link
        """
        url = 'https://foxmask.eu.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home,sweet,'

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def setUp(self):
        super(CommonStuffTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')


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


class PrivateLinksTestCase(CommonStuffTestCase):
    """
    Private Links for the current user
    """

    def test_private_links_list(self):
        self.create_link()
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/links/private/')
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
        request = RequestFactory().get('/links/public/')
        request.user = self.user

        view = PublicLinks.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class CreateLinksTestCase(CommonStuffTestCase):
    """
    Create Links from the form
    """
    def setUp(self):
        super(CommonStuffTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def create_link(self):
        """
        create a link
        """
        url = 'https://foxmask.eu.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home,sweet,'

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def test_get_the_form(self):
        template = "link_form.html"
        # Setup request and view.
        url_to_create = 'https://foxmask.eu.org/feeds/all.rss.xml'
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

    def test_create_link(self):
        url_to_create = 'https://foxmask.eu.org/a-propos.html#a-propos'
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
        self.create_link()
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
        # Setup request and view.
        url_to_create = 'https://foxmask.eu.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la passion'
        data = {
            'url': url_to_create,
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
        # Setup request and view.
        text = '# Le Free de la passion'
        data = {
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

    def create_links(self):
        url = 'https://foxmask.eu.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home,sweet,'
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def test_create3_drop_image(self):
        # create an entry into the model
        self.create_links()

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
        data = {'url': 'https://foxmask.eu.org/', 'tags': 'home,sweet,'}
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


class LinksByTagListTestCase(CommonStuffTestCase):
    """
    Deal with displaying Links for a given tag
    """

    def test_one_tag(self):
        self.create_link()
        template = "links_list.html"
        # Setup request and view.
        tags = 'foobar'

        request = RequestFactory().get(reverse('links_by_tag_list', kwargs={'tags': tags}))
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
        request = RequestFactory().get(reverse('links_by_tag_list', kwargs={'tags': '0Tag'}))
        tags = '0Tag'
        request.user = self.user
        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_public_links(self):
        # user object AnonymousUser + private = False
        self.create_link()
        template = "links_list.html"
        # Setup request and view.
        tags = 'home'

        request = RequestFactory().get(reverse('links_by_tag_list', kwargs={'tags': tags}))
        request.user = AnonymousUser()

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class TagsListTestCase(TestCase):
    """
    display the list of tags
    """

    def setUp(self):
        super(TagsListTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def create_links(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def create_links_no_tags(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky)

    def test_tag_index(self):
        self.create_links()
        self.create_links_no_tags()
        template = "tags_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('tags_list'))
        request.user = self.user
        view = TagsList.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class DailyListAnonymousTestCase(CommonStuffTestCase):
    """
    Home View for anonymous user
    """

    def setUp(self):
        super(DailyListAnonymousTestCase, self).setUp()
        self.factory = RequestFactory()

    def create_links_yesterday(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        today = datetime.now(timezone.utc).astimezone()
        yesterday = today - timedelta(days=1)
        Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                             date_created=yesterday)

    def create_links_today(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        today = datetime.now(timezone.utc).astimezone()
        Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                             date_created=today)

    def test_daily(self):
        self.create_links_today()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'))
        view = DailyLinks.as_view(template_name=template)
        request.user = AnonymousUser()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_previous(self):
        self.create_links_yesterday()
        today = date.today()
        yesterday = today - timedelta(days=1)
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'), kwargs={'yesterday': str(yesterday)})
        view = DailyLinks.as_view(template_name=template)
        request.user = AnonymousUser()
        # Run.
        response = view(request, yesterday=str(yesterday))
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class DailyLinksTestCase(TestCase):
    """
    Deal with Daily links
    """

    def setUp(self):
        super(DailyLinksTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def create_links_yesterday(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        today = datetime.now(timezone.utc).astimezone()
        yesterday = today - timedelta(days=1)
        Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                             date_created=yesterday)

    def create_links_today(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        today = datetime.now(timezone.utc).astimezone()
        Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                             date_created=today)

    def test_daily(self):
        self.create_links_today()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'))
        view = DailyLinks.as_view(template_name=template)
        request.user = self.user
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_previous(self):
        self.create_links_yesterday()
        today = date.today()
        yesterday = today - timedelta(days=1)
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'), kwargs={'yesterday': str(yesterday)})
        view = DailyLinks.as_view(template_name=template)
        request.user = self.user
        # Run.
        response = view(request, yesterday=str(yesterday))
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
