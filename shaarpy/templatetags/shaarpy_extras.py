# coding: utf-8
"""
ShaarPy :: Extra balls (because that reminds me pinball:)
"""

import markdown
from django import template
from django.urls import reverse

register = template.Library()


@register.filter(name="tags")
# draw the tags in the "card footer"
def tags(value: str) -> str:
    out = ""
    for tag in value.split(","):
        out += (
            '<a href="' + reverse("links_by_tag_list", args=[tag]) + '">'
            '<span class="badge rounded-pill text-bg-secondary">' + tag + "</span></a> "
        )

    return out


@register.filter(name="wrap_markdown")
def wrap_markdown(text: str) -> str:
    return markdown.markdown(text, extensions=["fenced_code", "codehilite", "footnotes", "tables"])
