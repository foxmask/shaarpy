# coding: utf-8
"""
    ShaarPy :: Importing in Netscape HTML File
"""

from django.core.management.base import BaseCommand
from rich.console import Console
from shaarpy.tools import import_shaarli

console = Console()

__author__ = 'FoxMaSk'


def load(html_file, reload_article_from_url):
    """
        load an HTML Nestcape file
    """
    if html_file.endswith('.html'):
        import_shaarli(html_file, reload_article_from_url)


class Command(BaseCommand):
    help = 'Import HTML Shaarli export file'

    def add_arguments(self, parser):
        parser.add_argument("file", help="provide the path to the HTM file to import", type=str)
        parser.add_argument("--reload", help="if you want to reload the article from the website", action='store_true')

    def handle(self, *args, **options):
        console.print(f"Shaarpy :: Importing file {options['file']} in progress", style="green")
        load(options['file'], options['reload'])
        console.print(f"Shaarpy :: Importing file {options['file']} is finished", style="green")
