# coding: utf-8
"""
   ShaarPy
"""
import datetime
from django.db import models
from django.urls import reverse


class Links(models.Model):
    tags = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(max_length=2048, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        verbose_name_plural = "Links"
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse('home')

