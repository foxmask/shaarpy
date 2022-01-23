# coding: utf-8
"""
    ShaarPy :: Admin
"""

from django.contrib import admin
from shaarpy.models import Links


class LinksAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'tags', 'date_created', 'private')
    search_fields = ['title', 'text', 'tags']


admin.site.register(Links, LinksAdmin)
