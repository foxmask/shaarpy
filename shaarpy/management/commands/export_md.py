# coding: utf-8
"""
    ShaarPy :: Exporting in markdown
"""
import os.path

from django.core.management.base import BaseCommand
from rich.console import Console
from shaarpy.models import Links
from shaarpy.tools import create_md_file
from slugify import slugify

console = Console()

__author__ = 'FoxMaSk'


class Command(BaseCommand):
    help = 'Export Shaarpy in Markdown files'

    def add_arguments(self, parser):
        parser.add_argument("folder", help="provide the path of the folder you want to export files", type=str)

    def handle(self, *args, **options):
        links = Links.objects.all()

        if os.path.exists(options['folder']):
            for link in links:
                file_name = slugify(link.title) + '.md'
                console.print(f"Shaarpy :: Exporting md file {options['folder']}/{file_name}", style="green")
                create_md_file(options['folder'],
                               link.title,
                               link.url,
                               link.text,
                               link.tags,
                               link.date_created,
                               link.private,
                               link.image,
                               link.video)
