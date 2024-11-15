# coding: utf-8
"""
    ShaarPy :: Extra balls (because that reminds me pinball:)
"""
import pypandoc
from django import template
from django.urls import reverse

register = template.Library()


@register.filter(name='tags')
# draw the tags in the "card footer"
def tags(value):
    out = ''
    for tag in value.split(','):
        out += '<a href="' + reverse('links_by_tag_list', args=[tag]) + '">' \
               '<span class="badge rounded-pill text-bg-secondary">' + tag + '</span></a> '

    return out


@register.filter(name='markdown')
def markdown(text):
    # convert into Github_Flavor_Markdown
    return pypandoc.convert_text(text, "html", format="gfm")
