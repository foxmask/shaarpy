# coding: utf-8
"""
ShaarPy :: Importing in Netscape HTML File
"""

import os

from django.core.management.base import BaseCommand
from rich.console import Console

from shaarpy.tools import import_shaarli

console = Console()

__author__ = "FoxMaSk"


class Command(BaseCommand):
    help = "Import HTML Shaarli export file"

    def add_arguments(self, parser):
        parser.add_argument("file", help="provide the path to the HTML file to import", type=str)
        parser.add_argument(
            "--reload",
            help="if you want to reload the article from the website",
            action="store_true",
        )

    def handle(self, *args, **options):
        file = options["file"]
        reload = options["reload"]
        console.print(f"Shaarpy :: Importing file {file} in progress", style="green")

        if os.path.exists(file) and file.endswith(".html"):
            import_shaarli(file, reload)
        else:
            console.print("provided file does not exists", style="red")

        console.print(f"Shaarpy :: Importing file {file} is finished", style="green")
