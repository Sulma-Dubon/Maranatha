from django.urls import path
from .views import experience_page, study_page, today_category_page

urlpatterns = [
    path('hoy/<slug:category_slug>/', today_category_page, name='today-category-page'),
    path('hoy/<slug:category_slug>/<str:version_abbr>/', today_category_page, name='today-category-version-page'),
    path('nfc/<str:public_uid>/', experience_page, name='nfc-public-page'),
    path('nfc/<str:public_uid>/study/', study_page, name='nfc-study-page'),
]
