from django.urls import path
from .views import nfc_experience_view

urlpatterns = [
    path('nfc/<str:public_uid>/', nfc_experience_view),
]
