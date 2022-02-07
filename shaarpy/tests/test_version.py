# coding: utf-8
"""
    ShaarPy
"""
from django.test import TestCase
import shaarpy


class VersionTestCase(TestCase):

    """
      check VERSION.txt
    """

    def test_version(self):

        self.assertIs(type(shaarpy.__version__), str)
