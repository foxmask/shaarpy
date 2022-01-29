# coding: utf-8
"""
    ShaarPy
"""
from django.test import TestCase
from shaarpy.models import Links


class LinksTest(TestCase):

    """
        Links Model
    """

    def create_link(self):

        url = 'https://foxmask.org/'
        title = 'Le Free de la passion'
        text = '# Le Free de la Passion'
        private = False
        sticky = True

        return Links.objects.create(url=url, title=title, text=text, private=private, sticky=sticky)

    def test_folders(self):
        inst = self.create_link()
        self.assertTrue(isinstance(inst, Links))
