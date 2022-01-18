# coding: utf-8
"""
    ShaarPy
"""
from datetime import datetime
from django.utils import timezone
from django.utils.text import Truncator
import html
from jinja2 import Environment, PackageLoader
from newspaper import Article
import os

import newspaper
import pypandoc
import re
from rich.console import Console
from rich.table import Table
from shaarpy import settings
from shaarpy.models import Links
from slugify import slugify

from urllib.parse import urlparse

console = Console()

"""
ARTICLES MANAGEMENT
"""


def _get_host(url):
    o = urlparse(url)
    return o.scheme + '://' + o.hostname


def _get_brand(url):
    brand = newspaper.build(_get_host(url))
    brand.download()
    brand.parse()
    return brand.brand


def grab_full_article(url):
    """
        get the complete article page from the URL
    """
    # get the complete article
    r = Article(url, keep_article_html=True)
    r.download()
    r.parse()
    # convert into markdown
    output = Truncator(r.article_html).chars("400", html=True)
    text = pypandoc.convert_text(output, 'md', format='html')
    title = r.title + ' - ' + _get_brand(url)
    return title, text


"""
MARKDOWN MANAGEMENT
"""


def rm_md_file(title):
    """
        rm a markdown file
    """
    file_name = slugify(title) + '.md'
    file_md = f'{settings.SHAARPY_LOCALSTORAGE_MD}/{file_name}'
    if os.path.exists(file_md):
        os.remove(file_md)


def create_md_file(title, url, text, tags, date_created, private):
    """
        create a markdown file
    """

    data = {'title': title,
            'url': url,
            'text': text,
            # 'date': datetime.now(),
            'date': date_created,
            'private': private,
            'tags': tags,
            'style': settings.SHAARPY_STYLE}

    env = Environment(
        loader=PackageLoader('shaarpy', 'templates'), autoescape=True
    )
    template = env.get_template('shaarpy/shaarpy_markdown.md')
    output = template.render(data=data)
    file_name = slugify(title) + '.md'
    file_md = f'{settings.SHAARPY_LOCALSTORAGE_MD}/{file_name}'
    # overwrite existing file with same slug name
    with open(file_md, 'w') as ls:
        ls.write(output)


def import_shaarli(the_file):
    private = 0
    with open(the_file, 'r') as f:
        data = f.read()

    if data.startswith('<!DOCTYPE NETSCAPE-Bookmark-file-1>'):
        i = 0
        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("Title", style="cyan")
        table.add_column("Private", style="yellow")
        table.add_column("Date", style="dim")

        for html_article in data.split('<DT>'):
            i += 1
            link = {'url': '',
                    'title': '',
                    'text': '',
                    'tags': '',
                    'date_created': '',
                    'private': False}
            if i == 1:
                continue

            for line in html_article.split('<DD>'):
                if line.startswith('<A '):
                    link['text'] = '' if line else html.unescape(line)
                    matches = re.match(r"<A (.*?)>(.*?)</A>", line)

                    attrs = matches[1]

                    link['title'] = matches[2] if matches[2] else ''
                    link['title'] = html.unescape(link['title'])

                    for attr in attrs.split(" "):
                        matches = re.match(r'([A-Z_]+)="(.+)"', attr)
                        attr_found = matches[1]
                        value_found = matches[2]
                        if attr_found == 'HREF':
                            link['url'] = html.unescape(value_found)
                        elif attr_found == 'ADD_DATE':
                            raw_add_date = int(value_found)
                            if raw_add_date > 30000000000:
                                raw_add_date /= 1000
                            link['date_created'] = datetime.fromtimestamp(raw_add_date).replace(tzinfo=timezone.utc)
                        elif attr == 'PRIVATE':
                            link['private'] = 0 if value_found == '0' else 1
                        elif attr == 'TAGS':
                            link['tags'] = html.unescape(value_found.replace(',', ' '))
                    if link['url'] != '':
                        if private:
                            link['private'] = 1

                        table.add_row(link['title'],
                                      "Yes" if link['private'] else "No",
                                      str(link['date_created']))

                        try:
                            obj = Links.objects.get(url=link['url'])
                            obj.title = link['title']
                            obj.text = link['text']
                            obj.tags = link['tags']
                            obj.private = private
                            obj.date_created = link['date_created']
                            obj.save()
                        except Links.DoesNotExist:
                            new_values = {'url': link['url'],
                                          'title': link['title'],
                                          'text': link['text'],
                                          'tags': link['tags'],
                                          'private': private,
                                          'date_created': link['date_created'],
                                          }
                            obj = Links(**new_values)
                            obj.save()

        console.print(table)
