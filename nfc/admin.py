from django.contrib import admin
from .models import NFCDevice, NFCScan

admin.site.register(NFCDevice)
admin.site.register(NFCScan)
