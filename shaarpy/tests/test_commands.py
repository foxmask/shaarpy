# coding: utf-8
"""
ShaarPy :: Test Management Commands
"""

from django.core.management import call_command
from django.test import TestCase

from shaarpy.models import Links


class CommandsExportMdTestCase(TestCase):
    def test_export_md(self):
        url = "https://foxmask.eu.org/"
        title = "Le Free de la passion"
        text = "# Le Free de la Passion"
        private = False
        sticky = True
        tags = "home,sweet,"

        Links.objects.create(
            url=url, title=title, text=text, private=private, sticky=sticky, tags=tags
        )

        call_command("export_md", "/tmp")


class CommandsImportPelicanTestCase(TestCase):
    def test_import_pelican(self):
        call_command("import_pelican", "shaarpy/tests/hacker-news-avec-django.md")


class CommandsImportPelicanDoesNotExistTestCase(TestCase):
    def test_import_pelican(self):
        call_command("import_pelican", "shaarpy/tests/filedoesnotexists.md")


class CommandsImportPelicanFolderTestCase(TestCase):
    def test_import_pelican_folder(self):
        call_command("import_pelican_folder", "shaarpy/tests/")


class CommandsImportPelicanDoesNotExistFolderTestCase(TestCase):
    def test_import_pelican_folder(self):
        call_command("import_pelican_folder", "shaarpy/fodlerdoesnotexists/")


class CommandsImportTestCase(TestCase):
    def test_import(self):
        call_command("import", "shaarpy/tests/bookmarks.html")


class CommandsImportDoesNotExistsTestCase(TestCase):
    def test_import(self):
        call_command("import", "shaarpy/tests/unexistingbookmarkfile.html")
