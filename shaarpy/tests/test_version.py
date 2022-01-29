# coding: utf-8
"""
    ShaarPy
"""
from django.test import TestCase
import shaarpy
import os


class VersionTestCase(TestCase):

    """
      check VERSION.txt
    """

    def test_version(self):
        assert os.path.isfile('VERSION.txt')
        self.assertIs(type(shaarpy.__version__), str)
