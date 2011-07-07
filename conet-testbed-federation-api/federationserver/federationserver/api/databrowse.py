from django.contrib import databrowse
from federationserver.api.models import *

databrowse.site.register(Federation)
databrowse.site.register(Project)
databrowse.site.register(Experiment)