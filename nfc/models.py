from django.db import models
from content.models import Verse
import random

EXPERIENCE_CHOICES = [
    ('DAILY', 'Versículo diario'),
    ('CATEGORY', 'Por categoría'),
    ('STATIC', 'Versículo estático'),
    ('STUDY', 'Estudio editable'),
]

class NFCDevice(models.Model):
    public_uid = models.CharField(max_length=100, unique=True)
    experience_type = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Devuelve un versículo estático
    def get_static_verse_data(self):
        verse = Verse.objects.filter(version__abbreviation='RVR1960').first()
        if verse:
            return {
                "book": verse.book.name,
                "chapter": verse.chapter,
                "verse_start": verse.verse_start,  # CORRECTO
                "verse_end": verse.verse_end,      # CORRECTO
                "text": verse.text,
            }
        return None

    # Devuelve un versículo diario (aleatorio por ahora)
    def get_daily_verse_data(self):
        verse = Verse.objects.filter(version__abbreviation='RVR1960').order_by('?').first()
        if verse:
            return {
                "book": verse.book.name,
                "chapter": verse.chapter,
                "verse_start": verse.verse_start,
                "verse_end": verse.verse_end,
                "text": verse.text,
            }
        return None


class NFCScan(models.Model):
    nfc_device = models.ForeignKey(NFCDevice, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)
    # opcional: podrías guardar IP, user_agent, etc.

    def __str__(self):
        return f"{self.nfc_device.public_uid} @ {self.scanned_at}"
