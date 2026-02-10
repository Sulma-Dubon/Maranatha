
from django.urls import path
from .views import PublicNFCView

urlpatterns = [
    path('<str:public_uid>/', PublicNFCView.as_view(), name='public-nfc'),
]
