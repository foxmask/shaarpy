# coding: utf-8
"""
    ShaarPy :: Test Managed Commands
"""
from django.core.management import call_command
from django.test import TestCase


class CommandsImportPelicanTestCase(TestCase):
    def test_import_pelican(self):
        " Import pelican"

        call_command('import_pelican', "tests/hacker-news-avec-django.md")


class CommandsImportPelicanDoesNotExistTestCase(TestCase):
    def test_import_pelican(self):
        " Import pelican"

        call_command('import_pelican', "tests/filedoesnotexists.md")


class CommandsImportPelicanFolderTestCase(TestCase):
    def test_import_pelican_folder(self):
        " Import pelican folder"

        call_command('import_pelican_folder', "tests/")


class CommandsImportPelicanDoesNotExistFolderTestCase(TestCase):
    def test_import_pelican_folder(self):
        " Import pelican folder"

        call_command('import_pelican_folder', "fodlerdoesnotexists/")
