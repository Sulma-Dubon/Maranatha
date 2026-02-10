
from django.urls import path
from .views import PublicNFCView, NFCConfigureView

urlpatterns = [
    path('configure/', NFCConfigureView.as_view(), name='nfc-configure'),
    path('<str:public_uid>/', PublicNFCView.as_view(), name='public-nfc'),
]
