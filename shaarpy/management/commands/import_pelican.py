# coding: utf-8
"""
ShaarPy :: Importing Pelican Markdown file
"""

import os

from django.core.management.base import BaseCommand
from rich.console import Console

from shaarpy.tools import import_pelican

console = Console()

__author__ = "FoxMaSk"


class Command(BaseCommand):
    help = "Import Pelican Markdown file"

    def add_arguments(self, parser):
        help = "provide the path to the Markdown file to import"
        parser.add_argument("file", help=help, type=str)

    def handle(self, *args, **options):
        md_file = options["file"]

        console.print(f"Shaarpy :: Importing file {md_file} in progress", style="green")

        if os.path.exists(md_file) and md_file.endswith(".md"):
            import_pelican(md_file)
        else:
            console.print("provided file does not exists", style="red")

        console.print(f"Shaarpy :: Importing file {md_file} is finished", style="green")
