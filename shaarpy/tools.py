# coding: utf-8
"""
    ShaarPy :: Tools

    - Importing/Exporting in Netscape HTML File
    - Load article from url with image/video
    - Manage Markdown file creation
"""
import base64
import copy
from bs4 import BeautifulSoup
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
    URL
"""


def url_cleaning(url):
    """
        drop unexpected content of the URL from the bookmarklet
    """
    if url:
        for pattern in ('&utm_source=', '?utm_source=', '&utm_medium=', '#xtor=RSS-'):
            pos = url.find(pattern)
            if pos > 0:
                url = url[0:pos]
    return url


"""
ARTICLES MANAGEMENT
"""


def _get_host(url):
    o = urlparse(url)
    hostname = o.scheme + '://' + o.hostname
    port = ''
    if o.port is not None and o.port != 80:
        port = ':' + str(o.port)
    hostname += port
    return hostname


def _get_brand(url):
    brand = newspaper.build(_get_host(url))
    brand.download()
    brand.parse()
    return brand.brand


def drop_image_node(content):
    my_image = ''
    soup = BeautifulSoup(content, 'html.parser')
    if soup.find_all('img', src=True):
        image = soup.find_all('img', src=True)[0]
        my_image = copy.copy(image['src'])
        # if not using copy.copy(image) before
        # image.decompose(), it drops content of the 2 vars
        # image and my_image
        image.decompose()
    return my_image, soup


def grab_full_article(url):
    """
        get the complete article page from the URL
    """
    # get the complete article
    r = Article(url, keep_article_html=True)
    try:
        r.download()
        r.parse()
        article_html = r.article_html
        video = r.movies[0] if len(r.movies) > 0 else ''
        image = ''
        # check if there is a top_image
        if r.top_image:
            # go to check image in the article_html and grab the first one found in article_html
            # it may happened that top_image is not the same in the content of article_html
            # so go pickup this one and remove it in the the content of article_html
            image, article_html = drop_image_node(article_html)
        # convert into markdown
        output = Truncator(article_html).chars("400", html=True)
        text = pypandoc.convert_text(output, 'md', format='html')
        title = r.title + ' - ' + _get_brand(url)

        return title, text, image, video
    except newspaper.article.ArticleException:
        return url, "", "", ""


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


def create_md_file(storage, title, url, text, tags, date_created, private, image, video):
    """
        create a markdown file
    """

    data = {'title': title,
            'url': url,
            'text': text,
            'date': date_created,
            'private': private,
            'tags': tags,
            'image': image,
            'video': video,
            'style': settings.SHAARPY_STYLE}

    env = Environment(
        loader=PackageLoader('shaarpy', 'templates'), autoescape=True
    )
    template = env.get_template('shaarpy/shaarpy_markdown.md')
    output = template.render(data=data)
    file_name = slugify(title) + '.md'
    file_md = f'{storage}/{file_name}'
    # overwrite existing file with same slug name
    with open(file_md, 'w') as ls:
        ls.write(output)


# CRC Stuff


def crc_that(string):
    """
    the PHP's hash(crc32) in Python :P

    implem in python:
       https://chezsoi.org/shaarli/shaare/U7admg
       https://stackoverflow.com/a/50843127/636849
    """
    a = bytearray(string, "utf-8")
    crc = 0xffffffff
    for x in a:
        crc ^= x << 24
        for k in range(8):
            crc = (crc << 1) ^ 0x04c11db7 if crc & 0x80000000 else crc << 1
    crc = ~crc
    crc &= 0xffffffff
    return int.from_bytes(crc.to_bytes(4, 'big'), 'little')


def small_hash(text):
    """
    Returns the small hash of a string, using RFC 4648 base64url format
   eg. smallHash('20111006_131924') --> yZH23w
   Small hashes:
     - are unique (well, as unique as crc32, at last)
     - are always 6 characters long.
     - only use the following characters: a-z A-Z 0-9 - _ @
     - are NOT cryptographically secure (they CAN be forged)
    In Shaarli, they are used as a tinyurl-like link to individual entries.
    """
    number = crc_that(text)

    number_bytes = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big')

    encoded = base64.b64encode(number_bytes)
    final_value = encoded.decode().rstrip('=').replace('+', '-').replace('/', '_')
    return final_value


# IMPORTING SHAARLI FILE

def import_shaarli(the_file, reload_article_from_url):  # noqa: C901
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
                    'image': None,
                    'video': None,
                    'date_created': '',
                    'private': False}
            if i == 1:
                continue

            if len(html_article.split('<DD>')) == 2:
                line, text = html_article.split('<DD>')
                link['text'] = html.unescape(text)

            for line in html_article.split('<DD>'):
                if line.startswith('<A '):
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
                            link['tags'] = value_found

                    if link['url'] != '' and link['url']:

                        if reload_article_from_url:
                            if link['url'].startswith('?'):
                                continue
                            link['title'], link['text'], link['image'], link['video'] = grab_full_article(link['url'])

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
                            obj.image = link['image']
                            obj.video = link['video']
                            obj.url_hashed = small_hash(link['date_created'].strftime("%Y%m%d_%H%M%S"))
                            obj.save()
                        except Links.DoesNotExist:
                            new_values = {'url': link['url'],
                                          'url_hashed': small_hash(link['date_created'].strftime("%Y%m%d_%H%M%S")),
                                          'title': link['title'],
                                          'text': link['text'],
                                          'tags': link['tags'],
                                          'private': private,
                                          'date_created': link['date_created'],
                                          'image': link['image'],
                                          'video': link['video'],
                                          }
                            obj = Links(**new_values)
                            obj.save()

        console.print(table)
