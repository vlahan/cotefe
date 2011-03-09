from django.contrib import databrowse
from testbedserver.taa.models import *

databrowse.site.register(User)
databrowse.site.register(Platform)
databrowse.site.register(Job)
