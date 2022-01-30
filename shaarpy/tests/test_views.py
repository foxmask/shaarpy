# coding: utf-8
"""
    ShaarPy
"""
from datetime import date, timedelta

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from django.urls import reverse

from shaarpy.forms import LinksForm
from shaarpy.models import Links
from shaarpy.views import HomeView, LinksCreate, LinksDetail, PrivateLinks, PublicLinks, LinksUpdate
from shaarpy.views import DailyLinks, TagsList, LinksByTagList, MeView, MeUpdate
from shaarpy.views import link_delete


# The functions

class ViewFunction(TestCase):

    def create_link(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home,sweet,'

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def setUp(self):
        super(ViewFunction, self).setUp()
        self.request = RequestFactory().get('/')
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_link_delete(self):
        link = self.create_link()
        # Setup request and view.
        request = RequestFactory().get('/')
        request.user = self.user
        response = link_delete(request=request, pk=link.id)
        # Check.
        self.assertEqual(response.status_code, 302)

    def test_link_delete_with_page(self):
        link = self.create_link()
        # Setup request and view.
        request = RequestFactory().get('/', {"page": "1"})
        request.user = self.user
        response = link_delete(request=request, pk=link.id)
        # Check.
        self.assertEqual(response.status_code, 302)


# CBV


class HomeViewTestCase(TestCase):

    def setUp(self):
        super(HomeViewTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_all_links_list(self):
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/')
        request.user = self.user

        view = HomeView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_search(self):
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/?q=foobar')
        request.user = self.user

        view = HomeView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_close_bookmarklet(self):
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/?source=bookmarklet')
        request.user = self.user

        view = HomeView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class HomeViewAnonymousTestCase(TestCase):

    def setUp(self):
        super(HomeViewAnonymousTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_all_links_list(self):
        template = "shaarpy/links_list.html"
        # Setup request and view.
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        view = HomeView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class PrivateLinksTestCase(TestCase):

    def setUp(self):
        super(PrivateLinksTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_private_links_list(self):
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


class PublicLinksTestCase(TestCase):

    def setUp(self):
        super(PublicLinksTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_private_links_list(self):
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


class CreateLinksTestCase(TestCase):

    def setUp(self):
        super(CreateLinksTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_get_the_form(self):
        template = "link_form.html"
        # Setup request and view.
        url_to_create = 'https://foxmask.org/feeds/all.rss.xml'
        title = 'Le Free de la passion'
        request = RequestFactory().get(reverse('link_create') + '?post=' + url_to_create + '&title=' + title)
        request.user = self.user
        view = LinksCreate.as_view(template_name=template)
        # Run.

        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_create(self):
        # Setup request and view.
        url_to_create = 'https://foxmask.org/feeds/all.rss.xml'
        title = 'Le Free de la passion'
        data = {
            'url': url_to_create,
            'title': title,
            'tags': 'home,sweet,',
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
        title = 'Le Free de la passion'
        text = '# Le Free de la passion'
        data = {
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
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home,sweet,'
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def test_create2(self):
        # create an entry into the model
        self.create_links()

        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
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
        data = {'url': 'https://foxmask.org/', 'tags': 'home,sweet,'}
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


class LinksDetailTestCase(TestCase):

    def create_links(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky)

    def setUp(self):
        super(LinksDetailTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_link_detail(self):
        link = self.create_links()
        template = "shaarpy/links_detail.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('link_detail', kwargs={'slug': link.url_hashed}))
        view = LinksDetail.as_view(template_name=template)
        # Run.
        response = view(request, pk=link.id)   # @TODO why pk=link.id and not slug=link.url_hashed ?
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class LinksUpdateTestCase(TestCase):

    def create_links(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky)

    def setUp(self):
        super(LinksUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_link_update(self):
        link = self.create_links()
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


class LinksByTagListTestCase(TestCase):

    def create_links(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags)

    def setUp(self):
        super(LinksByTagListTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_one_tag(self):
        link = self.create_links()
        template = "links_list.html"
        # Setup request and view.
        tags = link.tags

        request = RequestFactory().get(reverse('links_by_tag_list', kwargs={'tags': tags}))
        request.user = self.user

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_no_tag(self):
        self.create_links()

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
        link = self.create_links()
        template = "links_list.html"
        # Setup request and view.
        tags = link.tags

        request = RequestFactory().get(reverse('links_by_tag_list', kwargs={'tags': tags}))
        request.user = AnonymousUser()

        view = LinksByTagList.as_view(template_name=template)
        # Run.
        response = view(request, tags=tags)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class TagsListTestCase(TestCase):

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

    def setUp(self):
        super(TagsListTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

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


class DailyLinksTestCase(TestCase):

    def create_links(self):
        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True
        tags = 'home'
        today = date.today()
        yesterday = today - timedelta(days=1)

        Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                             date_created=yesterday)

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky, tags=tags,
                                    date_created=today)

    def setUp(self):
        super(DailyLinksTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_daily(self):
        self.create_links()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'))
        view = DailyLinks.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_previous(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        link = self.create_links()
        link.date_created = yesterday
        link.save()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('daily'), kwargs={'yesterday': str(yesterday)})
        view = DailyLinks.as_view(template_name=template)
        # Run.
        response = view(request, yesterday=str(yesterday))
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


# PROFILE


class MeTestCase(TestCase):

    def setUp(self):
        super(MeTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_me(self):
        template = "me.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('me'))
        request.user = self.user
        view = MeView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class MeUpdateTestCase(TestCase):

    def setUp(self):
        super(MeUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='foxmask', email='my@email.org', password='top_secret')

    def test_me(self):
        template = "edit_me.html"
        # Setup request and view.
        request = RequestFactory().get(reverse('edit_me'))
        request.user = self.user
        view = MeUpdate.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
