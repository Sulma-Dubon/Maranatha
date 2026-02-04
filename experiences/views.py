from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from nfc.models import NFCDevice, NFCScan
from .models import ExperienceConfig, StudyVerseAssignment
from content.models import Verse

import random


@api_view(['GET'])
def nfc_experience_view(request, public_uid):
    try:
        nfc = NFCDevice.objects.get(public_uid=public_uid, is_active=True)
    except NFCDevice.DoesNotExist:
        return Response(
            {'error': 'NFC no válido'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Registrar escaneo
    NFCScan.objects.create(nfc_device=nfc)

    # Obtener configuración
    config = ExperienceConfig.objects.filter(nfc_device=nfc).first()

    if nfc.experience_type == 'STATIC':
        verse = Verse.objects.first()

    elif nfc.experience_type == 'STUDY':
        assignment = StudyVerseAssignment.objects.filter(
            nfc_device=nfc
        ).first()
        if not assignment:
            return Response(
                {'error': 'Sin versículo asignado'},
                status=status.HTTP_404_NOT_FOUND
            )
        verse = assignment.verse

    elif nfc.experience_type in ['DAILY', 'CATEGORY']:
        queryset = Verse.objects.all()

        if config:
            queryset = queryset.filter(version=config.version)
            if config.category:
                queryset = queryset.filter(category=config.category)

        verse = random.choice(queryset)

    else:
        return Response(
            {'error': 'Tipo de experiencia no soportado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = {
        'book': verse.book.name,
        'chapter': verse.chapter,
        'verse': verse.verse_number,
        'text': verse.text,
    }

    return Response(data)
