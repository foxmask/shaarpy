# coding: utf-8
"""
ShaarPy :: Test Me
"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from shaarpy.views.me import Me, MeUpdate


class MeTestCase(TestCase):
    """
    test Me view
    """

    def setUp(self):
        super(MeTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="foxmask", email="my@email.org", password="top_secret"
        )

    def test_me(self):
        """
        test /me
        """
        template = "me.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("me"))
        request.user = self.user
        view = Me.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
        self.assertEqual(response.context_data["object"], self.user)

    def test_me_view_with_unauthenticated_user(self):
        request = self.factory.get(reverse("me"))
        request.user = AnonymousUser()

        response = Me.as_view()(request)
        # Check.
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class MeUpdateTestCase(TestCase):
    """
    test Me Update
    """

    def setUp(self):
        super(MeUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="foxmask", email="my@email.org", password="top_secret"
        )

    def test_me_update(self):
        """
        me view
        """
        template = "edit_me.html"
        # Setup request and view.
        request = RequestFactory().get(reverse("edit_me"))
        request.user = self.user
        view = MeUpdate.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], template)
        self.assertEqual(response.context_data["form"].instance, self.user)

    def test_me_update_view_with_unauthenticated_user(self):
        request = self.factory.get(reverse("edit_me"))
        request.user = AnonymousUser()

        response = MeUpdate.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_me_update_view_post(self):
        data = {"username": "foxmask", "password": "top_secretsecret"}
        request = self.factory.post(reverse("edit_me"), data=data)
        request.user = self.user

        response = MeUpdate.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("me"))

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "foxmask")
