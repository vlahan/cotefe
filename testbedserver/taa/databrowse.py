from django.contrib import databrowse
from testbedserver.taa.models import *

databrowse.site.register(UserProfile)
databrowse.site.register(Platform)
databrowse.site.register(Job)
