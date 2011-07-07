from django.contrib import admin
from federationserver.api.models import *

admin.site.register(Federation)
admin.site.register(Project)
admin.site.register(Experiment)
admin.site.register(Platform)
admin.site.register(Testbed)
admin.site.register(Testbed2Platform)