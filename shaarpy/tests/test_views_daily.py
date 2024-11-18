# coding: utf-8
"""
ShaarPy :: Test Daily Links
"""

from datetime import date, datetime, timedelta, timezone

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from shaarpy.models import Links
from shaarpy.views.daily import DailyLinks


class CommonDailyTestCase(TestCase):
    """
    Common fixtures
    """

    def create_links_today(self):
        url = "https://foxmask.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        tags = "home"
        today = datetime.now(tz=timezone.utc)
        Links.objects.create(
            url=url,
            title=title,
            text=text,
            private=private,
            sticky=sticky,
            tags=tags,
            date_created=today,
        )

    def create_links_before_yesterday(self):
        url = "https://foxmask.eu.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        tags = "home"
        today = datetime.now(tz=timezone.utc)
        yesterday = today - timedelta(days=2)
        Links.objects.create(
            url=url,
            title=title,
            text=text,
            private=private,
            sticky=sticky,
            tags=tags,
            date_created=yesterday,
        )

    def create_links_yesterday(self):
        url = "https://www.starlette.io/"
        title = " ✨ The little ASGI framework that shines. ✨ "
        text = "# Starlette is a lightweight ASGI framework/toolkit"
        private = False
        sticky = True
        tags = "home"
        today = datetime.now(tz=timezone.utc)
        yesterday = today - timedelta(days=1)
        Links.objects.create(
            url=url,
            title=title,
            text=text,
            private=private,
            sticky=sticky,
            tags=tags,
            date_created=yesterday,
        )

    def setUp(self):
        super(CommonDailyTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="foxmask", email="my@email.org", password="top_secret"
        )


class DailyListAnonymousTestCase(CommonDailyTestCase):
    """
    Home View for anonymous user
    """

    def setUp(self):
        super(DailyListAnonymousTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_daily(self):
        self.create_links_today()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("daily"))
        view = DailyLinks.as_view(template_name=template)
        request.user = AnonymousUser()
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_previous(self):
        self.create_links_before_yesterday()
        self.create_links_yesterday()
        today = date.today()
        yesterday = today - timedelta(days=1)
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("daily"), kwargs={"yesterday": str(yesterday)})
        view = DailyLinks.as_view(template_name=template)
        request.user = AnonymousUser()
        # Run.
        response = view(request, yesterday=str(yesterday))
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)


class DailyLinksTestCase(CommonDailyTestCase):
    """
    Deal with Daily links
    """

    def setUp(self):
        super(DailyLinksTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_daily(self):
        self.create_links_today()
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("daily"))
        view = DailyLinks.as_view(template_name=template)
        request.user = self.user
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)

    def test_previous(self):
        self.create_links_before_yesterday()
        self.create_links_yesterday()
        today = date.today()
        yesterday = today - timedelta(days=1)
        template = "daily_list.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("daily"), kwargs={"yesterday": str(yesterday)})
        view = DailyLinks.as_view(template_name=template)
        request.user = self.user
        # Run.
        response = view(request, yesterday=str(yesterday))
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
