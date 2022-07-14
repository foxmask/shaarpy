# coding: utf-8
"""
    ShaarPy :: Importing Pelican Markdown folder
"""

from django.core.management.base import BaseCommand
import os
from rich.console import Console
from shaarpy.tools import import_pelican_folder

console = Console()

__author__ = 'FoxMaSk'


def load_from_folder(folder):
    """
        load Pelican Markdown from a folder
    """
    if os.path.exists(folder):
        import_pelican_folder(folder)
    else:
        console.print("provided folder does not exists", style="red")


class Command(BaseCommand):
    help = 'Import Pelican Markdown folder'

    def add_arguments(self, parser):
        parser.add_argument("folder", help="provide the path to the Markdown folder", type=str)

    def handle(self, *args, **options):
        console.print(f"Shaarpy :: Importing folder {options['folder']} in progress", style="green")
        load_from_folder(options['folder'])
        console.print(f"Shaarpy :: Importing folder {options['folder']} is finished", style="green")
