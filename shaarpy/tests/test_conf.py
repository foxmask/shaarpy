# coding: utf-8
"""
ShaarPy :: Test Settings
"""

from django.conf import settings
from django.test import TestCase


class SettingsTestCase(TestCase):
    """
    check that all the needed config is present
    """

    def test_get_config_service(self):
        """
        check expecting config
        """
        self.assertIs(type(settings.SHAARPY_NAME), str)
        self.assertIs(type(settings.SHAARPY_DESCRIPTION), str)
        self.assertIs(type(settings.SHAARPY_AUTHOR), str)
        self.assertIs(type(settings.SHAARPY_ROBOT), str)
        self.assertIs(type(settings.SHAARPY_LOCALSTORAGE_MD), str)
        self.assertIs(type(settings.SHAARPY_STYLE), str)
        self.assertIs(type(settings.LANGUAGE_CODE), str)
        self.assertIs(type(settings.TIME_ZONE), str)
        self.assertIs(type(settings.USE_TZ), bool)
        self.assertIs(type(settings.ALLOWED_HOSTS), list)
        self.assertIs(type(settings.SECRET_KEY), str)
        self.assertIs(type(settings.CSRF_TRUSTED_ORIGINS), list)
