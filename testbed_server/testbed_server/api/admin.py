from django.contrib import admin
from django.contrib import databrowse
from api.models import Testbed, Platform, Job

admin.site.register(Testbed)
admin.site.register(Platform)
admin.site.register(Job)

databrowse.site.register(Testbed)
databrowse.site.register(Platform)
databrowse.site.register(Job)
