# coding: utf-8
"""
    ShaarPy :: Importing Pelican Markdown file
"""

import os

from django.core.management.base import BaseCommand
from rich.console import Console

from shaarpy.tools import import_pelican

console = Console()

__author__ = 'FoxMaSk'


def load(md_file):
    """
        load Pelican Markdown file
    """
    if os.path.exists(md_file) and md_file.endswith('.md'):
        import_pelican(md_file)
    else:
        console.print("provided file does not exists", style="red")


class Command(BaseCommand):
    help = 'Import Pelican Markdown file'

    def add_arguments(self, parser):
        parser.add_argument("file", help="provide the path to the Markdown file to import", type=str)

    def handle(self, *args, **options):
        console.print(f"Shaarpy :: Importing file {options['file']} in progress", style="green")
        load(options['file'])
        console.print(f"Shaarpy :: Importing file {options['file']} is finished", style="green")
