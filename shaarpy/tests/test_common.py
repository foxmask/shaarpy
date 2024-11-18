# coding: utf-8
"""
ShaarPy :: Test Common Stuff for any others TestCase
"""

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from shaarpy.models import Links


class CommonStuffTestCase(TestCase):
    """
    Common fixtures
    """

    def create_link(self):
        """
        create a link
        """
        url = "https://foxmask.eu.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        tags = "home,sweet,"

        return Links.objects.create(
            url=url, title=title, text=text, private=private, sticky=sticky, tags=tags
        )

    def setUp(self):
        super(CommonStuffTestCase, self).setUp()
        self.factory = RequestFactory()
        self.create_link()
        self.user = User.objects.create_user(
            username="foxmask", email="my@email.org", password="top_secret"
        )
