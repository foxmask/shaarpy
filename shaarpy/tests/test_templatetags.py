# coding: utf-8
"""
    ShaarPy :: Test templatetags rendering
"""

from django.test import TestCase
from django.template import Context, Template


class MyShaarpyExtrasTest(TestCase):

    def test_markdown(self):

        data = "# Test"
        out = Template(
            "{% load shaarpy_extras %}"
            "{{ '# Test' | markdown | safe}}"
        ).render(Context(data))
        self.assertEqual(out, '<h1 id="test">Test</h1>\n')

    def test_tags(self):
        out = ""
        data = "tags1,tags2"
        for tag in data.split(','):
            out += f'<a href="tags/{tag}"><span class="badge rounded-pill text-bg-secondary">{tag}</span></a> '

        out = Template(
            "{% load shaarpy_extras %}"
            "{{ 'tags1,tags2' | tags | safe}}"
        ).render(Context(data))
        self.assertEqual(out, '<a href="/tags/tags1"><span class="badge rounded-pill text-bg-secondary">tags1</span></a> <a href="/tags/tags2"><span class="badge rounded-pill text-bg-secondary">tags2</span></a> ')  # noqa
