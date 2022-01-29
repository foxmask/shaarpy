# coding: utf-8
"""
    ShaarPy
"""
from django.conf import settings
from django.test import TestCase
import os


class SettingsTestCase(TestCase):

    """
      check that all the needed config is present
    """

    def test_env_file(self):
        assert os.path.isfile('shaarpy/.env')

    def test_get_config_service(self):
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
