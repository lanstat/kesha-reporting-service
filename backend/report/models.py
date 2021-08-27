from django.db import models


class Report(models.Model):
    code = models.CharField(max_length=10, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
