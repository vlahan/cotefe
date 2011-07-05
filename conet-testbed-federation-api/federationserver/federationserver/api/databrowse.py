from django.contrib import databrowse
from api.models import *

databrowse.site.register(Federation)
databrowse.site.register(Project)
databrowse.site.register(Experiment)