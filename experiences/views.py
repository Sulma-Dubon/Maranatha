from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from nfc.models import NFCDevice
from content.models import Verse, VerseCategory

class ExperienceView(APIView):
    """
    Devuelve el contenido según la experiencia del NFCDevice:
    - STATIC: versículo fijo
    - DAILY: versículo diario aleatorio
    - CATEGORY: por categoría
    - STUDY: editable por el usuario
    """

    def get(self, request, public_uid):
        try:
            nfc_device = NFCDevice.objects.get(public_uid=public_uid, is_active=True)
        except NFCDevice.DoesNotExist:
            return Response({"detail": "NFC no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "public_uid": nfc_device.public_uid,
            "experience_type": nfc_device.experience_type,
            "verse_data": None,
        }

        # STATIC → primer versículo RVR1960 por ejemplo
        if nfc_device.experience_type == 'STATIC':
            verse = Verse.objects.filter(version__abbreviation='RVR1909').first()
            if verse:
                data['verse_data'] = {
                    'book': verse.book.name,
                    'chapter': verse.chapter,
                    'verse_start': verse.verse_start,
                    'verse_end': verse.verse_end,
                    'text': verse.text,
                }

        # DAILY → versículo aleatorio RVR1960
        elif nfc_device.experience_type == 'DAILY':
            verse = Verse.objects.filter(version__abbreviation='RVR1960').order_by('?').first()
            if verse:
                data['verse_data'] = {
                    'book': verse.book.name,
                    'chapter': verse.chapter,
                    'verse_start': verse.verse_start,
                    'verse_end': verse.verse_end,
                    'text': verse.text,
                }

        # CATEGORY → aleatorio dentro de una categoría (ejemplo: 'amor')
        elif nfc_device.experience_type == 'CATEGORY':
            category = VerseCategory.objects.first()  # aquí puedes cambiar a la categoría deseada
            verse = Verse.objects.filter(categories=category).order_by('?').first()
            if verse:
                data['verse_data'] = {
                    'book': verse.book.name,
                    'chapter': verse.chapter,
                    'verse_start': verse.verse_start,
                    'verse_end': verse.verse_end,
                    'text': verse.text,
                    'category': category.name,
                }

        # STUDY → editable por el usuario, aquí se podría retornar el versículo actual asignado
        elif nfc_device.experience_type == 'STUDY':
            # Por ahora, ejemplo simple: mismo que STATIC
            verse = Verse.objects.filter(version__abbreviation='RVR1960').first()
            if verse:
                data['verse_data'] = {
                    'book': verse.book.name,
                    'chapter': verse.chapter,
                    'verse_start': verse.verse_start,
                    'verse_end': verse.verse_end,
                    'text': verse.text,
                }

        return Response(data, status=status.HTTP_200_OK)
