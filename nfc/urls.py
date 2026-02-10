
from django.urls import path
from .views import PublicNFCView, NFCConfigureView

urlpatterns = [
    path('<str:public_uid>/', PublicNFCView.as_view(), name='public-nfc'),
    path('configure/', NFCConfigureView.as_view(), name='nfc-configure'),
]
