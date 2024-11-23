# coding: utf-8
"""
ShaarPy :: Importing Pelican Markdown folder
"""

import os

from django.core.management.base import BaseCommand
from rich.console import Console

from shaarpy.tools import import_pelican_folder

console = Console()

__author__ = "FoxMaSk"


class Command(BaseCommand):
    help = "Import Pelican Markdown folder"

    def add_arguments(self, parser):
        parser.add_argument("folder", help="provide the path to the Markdown folder", type=str)

    def handle(self, *args, **options):
        folder = options["folder"]
        console.print(f"Shaarpy :: Importing folder {folder} in progress", style="green")

        if os.path.exists(folder):
            import_pelican_folder(folder)
        else:
            console.print("provided folder does not exists", style="red")

        console.print(f"Shaarpy :: Importing folder {folder} is finished", style="green")
