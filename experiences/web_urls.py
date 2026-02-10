from django.urls import path
from .views import experience_page, study_page

urlpatterns = [
    path('nfc/<str:public_uid>/', experience_page, name='nfc-public-page'),
    path('nfc/<str:public_uid>/study/', study_page, name='nfc-study-page'),
]
