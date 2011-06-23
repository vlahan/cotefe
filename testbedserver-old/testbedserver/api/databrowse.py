from django.contrib import databrowse
from testbedserver.api.models import *

databrowse.site.register(UserResource)
databrowse.site.register(TestbedResource)
databrowse.site.register(PlatformResource)
databrowse.site.register(NodeResource)
databrowse.site.register(NodeGroupResource)
databrowse.site.register(ImageResource)
databrowse.site.register(JobResource)