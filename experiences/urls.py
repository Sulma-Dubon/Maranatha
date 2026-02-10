from django.urls import path
from .views import ExperienceView, VerseListView, StudyVerseAddView

urlpatterns = [
    path('nfc/<str:public_uid>/', ExperienceView.as_view()),
    path('verses/', VerseListView.as_view()),
    path('nfc/<str:public_uid>/study/add/', StudyVerseAddView.as_view()),
]

