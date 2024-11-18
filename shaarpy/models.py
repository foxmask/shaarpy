# coding: utf-8
"""
ShaarPy :: Models
"""

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

# Regex to match latin and 한글 (hangul) chars
alphanum_hangul = RegexValidator(
    r"^[0-9a-zA-Z\u3131-\uD79D\u1100-\u11FF\u3130-\u318F\uA960-\uA97F\uAC00-\uD7AF\uD7B0-\uD7FF,]*$",
    "Only alphanumeric characters are allowed.",
)


class Links(models.Model):
    """
    Links model to handle URLs / notes
    """

    tags = models.CharField(max_length=255, null=True, blank=True, validators=[alphanum_hangul])
    url = models.URLField(max_length=2048, null=True, blank=True)
    url_hashed = models.SlugField(max_length=10, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    video = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    sticky = models.BooleanField(default=False)

    class Meta:
        """
        Meta properties
        """

        verbose_name_plural = "Links"
        ordering = ["-sticky", "-date_created"]
