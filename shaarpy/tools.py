from django.utils.text import Truncator
from jinja2 import Environment, PackageLoader
from newspaper import Article
import os

import newspaper
import pypandoc

from shaarpy import settings
from slugify import slugify

from urllib.parse import urlparse


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
