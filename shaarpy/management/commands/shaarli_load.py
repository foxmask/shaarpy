# coding: utf-8
"""
Shaarpy :: loading Shaarpi html exported file
"""

from django.core.management.base import BaseCommand
from rich.console import Console
from shaarpy.tools import import_shaarli

console = Console()

__author__ = 'FoxMaSk'


def load(html_file):
    """
        load an HTML Nestcape file
    """
    if html_file.endswith('.html'):
        import_shaarli(html_file)


class Command(BaseCommand):
    help = 'Import HTML Shaarli export file'

    def add_arguments(self, parser):
        parser.add_argument("file", help="provide the path to the HTM file to import", type=str)

    def handle(self, *args, **options):
        console.print(f"Shaarpy :: Importing file {options['file']} in progress", style="green")
        load(options['file'])
        console.print(f"Shaarpy :: Importing file {options['file']} is finished", style="green")
