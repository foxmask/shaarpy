# coding: utf-8
"""
    ShaarPy :: Extra balls (because that reminds me pinball:)
"""
from django.urls import reverse
from django import template
import pypandoc

register = template.Library()


@register.filter(name='tags')
# draw the tags in the "card footer"
def tags(value):
    out = ''
    for tag in value.split(','):
        out += '<a href="' + reverse('links_by_tag_list', args=[tag]) + '">' \
               '<span class="badge rounded-pill bg-secondary">' + tag + '</span></a> '

    return out


@register.filter(name='markdown')
def markdown(text):
    # convert into Github_Flavor_Markdown
    return pypandoc.convert_text(text, "html", format="gfm")
