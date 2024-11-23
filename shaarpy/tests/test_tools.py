# coding: utf-8
"""
ShaarPy :: Test Tools
"""

from django.test import TestCase

from shaarpy.tools import _get_brand, _get_host


class ToolsTest(TestCase):
    def test_get_host(self):
        host = "https://wikipedia.org"
        x = _get_host(host)
        self.assertIsInstance(x, str)

    def test_get_host_with_port(self):
        host = "https://wikipedia.org:443"
        x = _get_host(host)
        self.assertIsInstance(x, str)

    def test_get_brand(self):
        url = "https://wikipedia.org:443"
        x = _get_brand(url)
        self.assertIsInstance(x, str)
