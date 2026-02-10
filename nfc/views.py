
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import NFCDevice
from .serializers import PublicNFCSerializer

class PublicNFCView(RetrieveAPIView):
    queryset = NFCDevice.objects.filter(is_active=True)
    serializer_class = PublicNFCSerializer
    lookup_field = 'public_uid'

    def get(self, request, *args, **kwargs):
        try:
            nfc_device = self.get_object()
        except NFCDevice.DoesNotExist:
            return Response({"detail": "NFC no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(nfc_device)
        return Response(serializer.data)
