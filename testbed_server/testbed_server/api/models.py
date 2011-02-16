from django.db import models
from django.contrib.auth.models import User

class Testbed(models.Model):
    uri = models.CharField(max_length=255)
    media_type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)

class Job(models.Model):
    uri = models.CharField(max_length=255)
    media_type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User)