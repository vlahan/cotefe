from django.contrib import admin
from django.contrib import databrowse
from api.models import *

admin.site.register(Testbed)
admin.site.register(Job)

databrowse.site.register(Testbed)
databrowse.site.register(Job)
