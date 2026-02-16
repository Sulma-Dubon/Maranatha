
from django.conf import settings
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import NFCDevice, NFCScan
from .serializers import PublicNFCSerializer
from experiences.models import ExperienceConfig
from content.models import BibleVersion, VerseCategory, Verse

class PublicNFCView(RetrieveAPIView):
    queryset = NFCDevice.objects.filter(is_active=True)
    serializer_class = PublicNFCSerializer
    lookup_field = 'public_uid'

    def get(self, request, *args, **kwargs):
        try:
            nfc_device = self.get_object()
        except NFCDevice.DoesNotExist:
            return Response({"detail": "NFC no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if settings.ENABLE_NFC_SCAN_LOGS:
            NFCScan.objects.create(nfc_device=nfc_device)

        serializer = self.get_serializer(nfc_device)
        return Response(serializer.data)


class NFCConfigureView(APIView):
    def post(self, request):
        public_uid = request.data.get('public_uid')
        experience_type = request.data.get('experience_type')
        version_abbr = request.data.get('version')
        category_slug = request.data.get('category')
        static_verse_id = request.data.get('static_verse_id')
        is_active = request.data.get('is_active', True)

        if not public_uid:
            return Response({"detail": "public_uid es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        if not experience_type:
            return Response({"detail": "experience_type es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        if not version_abbr:
            return Response({"detail": "version es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        version = BibleVersion.objects.filter(abbreviation=version_abbr).first()
        if not version:
            return Response({"detail": "Version no encontrada"}, status=status.HTTP_400_BAD_REQUEST)

        category = None
        static_verse = None

        if experience_type == 'CATEGORY':
            if not category_slug:
                return Response({"detail": "category es requerido para CATEGORY"}, status=status.HTTP_400_BAD_REQUEST)
            category = VerseCategory.objects.filter(slug=category_slug).first()
            if not category:
                return Response({"detail": "Categoria no encontrada"}, status=status.HTTP_400_BAD_REQUEST)
            if not Verse.objects.filter(categories=category, version=version).exists():
                return Response(
                    {"detail": "La categoria no tiene versiculos en la version seleccionada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif experience_type == 'STATIC':
            if not static_verse_id:
                return Response({"detail": "static_verse_id es requerido para STATIC"}, status=status.HTTP_400_BAD_REQUEST)
            static_verse = Verse.objects.filter(id=static_verse_id).select_related('version').first()
            if not static_verse:
                return Response({"detail": "Versiculo no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
            if static_verse.version_id != version.id:
                return Response({"detail": "Versiculo no pertenece a la version seleccionada"}, status=status.HTTP_400_BAD_REQUEST)
        elif experience_type == 'STUDY':
            category = VerseCategory.objects.filter(slug='general').first()
            if not category:
                return Response({"detail": "Categoria general no existe"}, status=status.HTTP_400_BAD_REQUEST)
            if not Verse.objects.filter(categories=category, version=version).exists():
                return Response(
                    {"detail": "Categoria general no tiene versiculos en la version seleccionada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif experience_type == 'DAILY':
            if not Verse.objects.filter(version=version).exists():
                return Response(
                    {"detail": "La version no tiene versiculos cargados"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response({"detail": "experience_type invalido"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            nfc_device, _ = NFCDevice.objects.get_or_create(public_uid=public_uid)
            nfc_device.experience_type = experience_type
            nfc_device.is_active = bool(is_active)
            nfc_device.save()

            config, _ = ExperienceConfig.objects.get_or_create(nfc_device=nfc_device)
            config.version = version
            config.category = category
            config.static_verse = static_verse
            config.is_editable = (experience_type == 'STUDY')
            config.save()

        return Response(
            {
                "public_uid": nfc_device.public_uid,
                "experience_type": nfc_device.experience_type,
                "version": version.abbreviation,
                "category": category.slug if category else None,
                "static_verse_id": static_verse.id if static_verse else None,
                "is_active": nfc_device.is_active,
            },
            status=status.HTTP_200_OK,
        )
