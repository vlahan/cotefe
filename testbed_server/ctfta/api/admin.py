from django.contrib import admin
from django.contrib import databrowse
from ctfta.api.models import Platform, Job

admin.site.register(Platform)
admin.site.register(Job)

databrowse.site.register(Platform)
databrowse.site.register(Job)
