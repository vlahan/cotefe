from django.contrib import admin
from testbedserver.api.models import *

admin.site.register(UserResource)
admin.site.register(TestbedResource)
admin.site.register(PlatformResource)
admin.site.register(NodeResource)
admin.site.register(NodeGroupResource)
admin.site.register(ImageResource)
admin.site.register(JobResource)