# coding: utf-8
"""
    ShaarPy :: Models
"""
import datetime
from django.db import models


class Links(models.Model):
    tags = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(max_length=2048, null=True, blank=True)
    url_hashed = models.SlugField(max_length=10, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    video = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    sticky = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Links"
        ordering = ['-sticky', '-date_created']
