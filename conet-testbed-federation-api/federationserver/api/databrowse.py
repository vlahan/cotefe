from django.contrib import databrowse

try:
    from federationserver.api.models import *
except ImportError:
    from api.models import *

databrowse.site.register(Federation)
databrowse.site.register(Project)
databrowse.site.register(Experiment)