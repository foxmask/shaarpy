
from django import template
import pypandoc

register = template.Library()


@register.filter(name='tags')
def tags(value):
    out = ''
    for tag in value.split(','):
        out += f'<a href="/links/{tag}"><span class="badge rounded-pill bg-secondary">{tag}</span></a> '
    return out


@register.filter(name='markdown')
def makrdown(text):
    return pypandoc.convert_text(text, "html", format="md")


