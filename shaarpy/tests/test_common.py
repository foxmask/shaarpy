# coding: utf-8
"""
ShaarPy :: Test Common Stuff for any others TestCase
"""

from django.contrib.auth.models import Permission, User
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
        self.link = self.create_link()

        # create a user
        self.user = User.objects.create_user(
            username="foxmask", email="my@email.org", password="top_secret"
        )
        # set permission
        permission = Permission.objects.get(codename="view_private_links")
        # add that permission to the user
        self.user.user_permissions.add(permission)

        # create a user w/o perms
        self.user_no_perm = User.objects.create_user(
            username="foxmask2", email="my2@email.org", password="top_secret2"
        )
