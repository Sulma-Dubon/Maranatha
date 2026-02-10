from django.urls import path
from .views import ExperienceView

urlpatterns = [
    path('nfc/<str:public_uid>/', ExperienceView.as_view()),
]

