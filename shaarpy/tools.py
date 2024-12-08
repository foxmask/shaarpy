# coding: utf-8
"""
ShaarPy :: Tools

- Importing/Exporting in Netscape HTML File
- Load article from url with image/video
- Manage Markdown file creation
"""

import base64
import html
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, PackageLoader
from rich.console import Console
from rich.table import Table
from slugify import slugify

from shaarpy import settings
from shaarpy.models import Links

console = Console()
logger = logging.getLogger("tools")


def is_valid_date(date_str: str, date_format: str) -> bool | None:
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


"""
    URL
"""


def url_cleaning(url: str) -> str:
    """
    drop unexpected content of the URL from the bookmarklet

    param url: url of the website
    :return string url
    """

    if url:
        for pattern in ("&utm_source=", "?utm_source=", "&utm_medium=", "#xtor=RSS-"):
            pos = url.find(pattern)
            if pos > 0:
                url = url[0:pos]
    return url


# MARKDOWN MANAGEMENT


def create_md_file(
    storage: str,
    title: str,
    url: str,
    text: str,
    tags: str,
    date_created: str,
    private: bool,
    image: str,
    video: str,
) -> None:
    """
        create a markdown file
    storage: path of the folder where to store the file
    title: title of the file
    url: url of the article
    text: text of the article
    tags: tags if provided
    date_created: creation date
    private: boolean true/false
    image: the main image if any
    video: the main video if any
    """

    data = {
        "title": title,
        "url": url,
        "text": text,
        "date": date_created,
        "private": private,
        "tags": tags,
        "image": image,
        "video": video,
        "author": settings.SHAARPY_AUTHOR,
        "style": settings.SHAARPY_STYLE,
    }

    env = Environment(loader=PackageLoader("shaarpy", "templates"), autoescape=True)
    template = env.get_template("shaarpy_markdown.md")
    output = template.render(data=data)
    file_name = slugify(title) + ".md"
    file_md = f"{storage}/{file_name}"
    # overwrite existing file with same slug name
    with open(file_md, "w") as ls:
        ls.write(output)


# CRC Stuff


def crc_that(string: str) -> int:
    """
    the PHP's hash(crc32) in Python :P

    implem in python:
       https://chezsoi.org/shaarli/shaare/U7admg
       https://stackoverflow.com/a/50843127/636849
    """
    a = bytearray(string, "utf-8")
    crc = 0xFFFFFFFF
    for x in a:
        crc ^= x << 24
        for k in range(8):
            crc = (crc << 1) ^ 0x04C11DB7 if crc & 0x80000000 else crc << 1
    crc = ~crc
    crc &= 0xFFFFFFFF
    return int.from_bytes(crc.to_bytes(4, "big"), "little")


def small_hash(text: str) -> str:
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

    number_bytes = number.to_bytes((number.bit_length() + 7) // 8, byteorder="big")

    encoded = base64.b64encode(number_bytes)
    final_value = encoded.decode().rstrip("=").replace("+", "-").replace("/", "_")
    return final_value


# IMPORTING SHAARLI FILE


def import_shaarli(the_file: str, reload_article_from_url: str) -> None:  # noqa
    """
    the_file: name of the file to import
    reload_article_from_url: article url
    """
    private = 0
    date_created: datetime

    with open(the_file, "r") as f:
        data = f.read()
        msg = f"ShaarPy :: importing {the_file}"
        logger.debug(msg)

    if data.startswith("<!DOCTYPE NETSCAPE-Bookmark-file-1>"):
        i = 0
        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("Title", style="cyan")
        table.add_column("Private", style="yellow")
        table.add_column("Date", style="dim")

        for html_article in data.split("<DT>"):
            i += 1
            link = {
                "url": "",
                "title": "",
                "text": "",
                "tags": "",
                "image": None,
                "video": None,
                "private": False,
            }
            if i == 1:
                continue

            if len(html_article.split("<DD>")) == 2:
                line, text = html_article.split("<DD>")
                link["text"] = html.unescape(text)

            for line in html_article.split("<DD>"):
                if line.startswith("<A "):
                    matches = re.match(r"<A (.*?)>(.*?)</A>", line)
                    if matches:
                        attrs = matches.group(1)

                        link["title"] = matches.group(2) if matches.group(2) else ""
                        link["title"] = html.unescape(str(link["title"]))

                    for attr in attrs.split(" "):
                        matches = re.match(r'([A-Z_]+)="(.+)"', attr)
                        attr_found = matches.group(1) if matches else ""
                        value_found = matches.group(2) if matches else ""
                        if attr_found == "HREF":
                            link["url"] = html.unescape(value_found)
                        elif attr_found == "ADD_DATE":
                            raw_add_date = float(value_found)
                            if raw_add_date > 30000000000:
                                raw_add_date /= 1000
                            date_created = datetime.fromtimestamp(raw_add_date).replace(
                                tzinfo=timezone.utc
                            )
                        elif attr == "PRIVATE":
                            link["private"] = False if value_found == "0" else True
                        elif attr == "TAGS":
                            link["tags"] = value_found

                    if link["url"] != "" and link["url"]:
                        if reload_article_from_url:
                            if str(link["url"]).startswith("?"):
                                continue

                        if private:
                            link["private"] = True

                        table.add_row(
                            str(link["title"]),
                            "Yes" if link["private"] else "No",
                            str(date_created),
                        )

                        to_hash = date_created.strftime("%Y%m%d_%H%M%S")

                        try:
                            obj = Links.objects.get(url=link["url"])
                            obj.title = str(link["title"])
                            obj.text = str(link["text"])
                            obj.tags = str(link["tags"])
                            obj.private = bool(private)
                            obj.date_created = date_created
                            obj.image = str(link["image"])
                            obj.video = str(link["video"])
                            obj.url_hashed = small_hash(to_hash)
                            msg = f"ShaarPy :: updating {obj.url}"
                            logger.debug(msg)
                            obj.save()
                        except Links.DoesNotExist:
                            new_values = {
                                "url": link["url"],
                                "url_hashed": small_hash(to_hash),
                                "title": link["title"],
                                "text": link["text"],
                                "tags": link["tags"],
                                "private": private,
                                "date_created": date_created,
                                "image": link["image"],
                                "video": link["video"],
                            }
                            obj = Links(**new_values)
                            obj.save()
                            msg = f"ShaarPy :: creating {obj.url}"
                            logger.debug(msg)

        console.print(table)


# IMPORTING PELICAN FILE


def import_pelican(the_file: str) -> None:  # noqa
    """
    Headers are :

    Title: Home Sweet Home
    Date: 2021-09-27
    Author: foxmask
    Category: Korea
    Tags: hosting, Korea
    Slug: home-sweet-home
    Status: published
    Summary: text

    body content

    the_file: path of the file to create
    """
    private: bool = False
    my_title: str
    date_created: datetime
    slug: str
    tags: str
    url_hashed: str
    text: str = ""
    status: str = ""
    summary: str = ""
    author: str = ""
    allowed_sections = (
        "Author: ",
        "Status: ",
        "Title: ",
        "Date: ",
        "Tags: ",
        "Slug: ",
        "Summary: ",
    )

    with open(the_file, "r") as f:
        data = f.readlines()
        msg = f"ShaarPy :: importing {the_file}"
        logger.debug(msg)

        for line in data:
            if line.title().startswith("Author: "):
                author = line.title().split("Author: ")[1].strip()
                author = f"</br>By {author}"
            if line.title().startswith("Status: "):
                status = line.title().split("Status: ")[1].strip()
            if line.title().startswith("Title: "):
                my_title = line.title().split("Title: ")[1].strip()
            if line.title().startswith("Date: "):
                date_created_str = line.title().split("Date: ")[1].strip()

                if len(date_created_str) == 10:
                    # date without hours minutes secondes
                    date_created_str += " 00:00:00"
                elif len(date_created_str) == 16:
                    # date with hours minutes
                    date_created_str += ":00"

                if is_valid_date(date_created_str, "%Y-%m-%d %H:%M:%S"):
                    date_created = datetime.strptime(date_created_str, "%Y-%m-%d %H:%M:%S")
                elif is_valid_date(date_created_str, "%Y-%m-%d %H:%M:%S%z"):
                    date_created = datetime.strptime(date_created_str, "%Y-%m-%d %H:%M:%S%z")
                elif is_valid_date(date_created_str, "%Y-%m-%d %H:%M:%S.%f%z"):
                    date_created = datetime.strptime(date_created_str, "%Y-%m-%d %H:%M:%S.%f%z")
            # to handle "Tags: " or "tags: "
            if line.title().startswith("Tags: "):
                tags = line.title().split("Tags: ")[1].strip()

                unwanted_chars = "?./:;!#&@{}[]|`\\^~*+=-_"

                if any(s in unwanted_chars for s in tags):
                    tags = ""

                if tags.endswith(","):
                    tags = tags[:-1]
                tags = tags.replace(" ", "")

            if line.title().startswith("Slug: "):
                slug = line.title().split("Slug: ")[1].strip()
            if line.title().startswith("Summary: "):
                summary = "# " + line.title().split("Summary: ")[1] + "\n\n"
            if status == "published":
                url_hashed = small_hash(date_created.strftime("%Y%m%d_%H%M%S"))

            if not line.title().startswith(allowed_sections):
                text += summary
            if author:
                text += author

    if status == "published":
        try:
            Links.objects.get(url_hashed=url_hashed)
            console.print(f"Shaarpy :: {my_title} already exists", style="yellow")
        except Links.DoesNotExist:
            Links.objects.create(
                title=my_title,
                tags=tags,
                url=slug,
                url_hashed=url_hashed,
                text=text,
                date_created=date_created,
                private=bool(private),
            )
            console.print(f"Shaarpy :: {my_title} added", style="magenta")


def import_pelican_folder(folder: str) -> None:
    """
    folder: folder path where to find md file to import
    """

    for p in Path(folder).glob("*.md"):
        import_pelican(folder + "/" + p.name)
