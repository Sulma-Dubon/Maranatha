from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/nfc/', include('nfc.urls')),
    path('api/', include('experiences.urls')),
    path('', include('experiences.web_urls')),
]
