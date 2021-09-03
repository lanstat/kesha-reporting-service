from django.db import models


class Font(models.Model):
    family = models.CharField(max_length=100)
    style = models.CharField(max_length=30)
    source = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
