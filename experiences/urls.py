from django.urls import path
from .views import (
    ExperienceView,
    CategoryTodayView,
    VerseListView,
    StudyVerseAddView,
    VersionsView,
    CategoriesView,
    ExperienceTypesView,
)

urlpatterns = [
    path('nfc/<str:public_uid>/', ExperienceView.as_view()),
    path('today/<slug:category_slug>/', CategoryTodayView.as_view()),
    path('today/<slug:category_slug>/<str:version_abbr>/', CategoryTodayView.as_view()),
    path('verses/', VerseListView.as_view()),
    path('nfc/<str:public_uid>/study/add/', StudyVerseAddView.as_view()),
    path('versions/', VersionsView.as_view()),
    path('categories/', CategoriesView.as_view()),
    path('experience-types/', ExperienceTypesView.as_view()),
]

