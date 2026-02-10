from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from content.models import Verse

EXPERIENCE_CHOICES = [
    ('DAILY', 'VersÃ­culo diario'),
    ('CATEGORY', 'Por categorÃ­a'),
    ('STATIC', 'VersÃ­culo estÃ¡tico'),
    ('STUDY', 'Estudio editable'),
]


class NFCDevice(models.Model):
    public_uid = models.CharField(max_length=100, unique=True)
    experience_type = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="nfc_devices",
    )

    def _build_verse_data(self, verse, category=None):
        if not verse:
            return None
        data = {
            "book": verse.book.name,
            "chapter": verse.chapter,
            "verse_start": verse.verse_start,
            "verse_end": verse.verse_end,
            "text": verse.text,
        }
        if category:
            data["category"] = category.name
        return data

    # Devuelve un versÃ­culo estÃ¡tico
    def get_static_verse_data(self, verse=None, version=None):
        if verse:
            return self._build_verse_data(verse)
        if not version:
            return None
        version_abbr = version
        verse = Verse.objects.filter(version__abbreviation=version_abbr).order_by('id').first()
        return self._build_verse_data(verse)

    # Devuelve un versÃ­culo diario (deterministico por fecha)
    def get_daily_verse_data(self, version=None):
        if not version:
            return None
        version_abbr = version
        qs = Verse.objects.filter(version__abbreviation=version_abbr).order_by('id')
        count = qs.count()
        if count == 0:
            return None
        index = timezone.localdate().toordinal() % count
        verse = qs[index]
        return self._build_verse_data(verse)

    # Devuelve un versÃ­culo por categoria (aleatorio por ahora)
    def get_category_verse_data(self, category, version=None):
        if not category:
            return None
        day_key = timezone.localdate().isoformat()
        if not version:
            return None
        version_abbr = version
        cache_key = f"daily_verse:{category.id}:{version_abbr}:{day_key}"
        verse_id = cache.get(cache_key)
        if verse_id is None:
            verse = (
                Verse.objects.filter(version__abbreviation=version_abbr, categories=category)
                .order_by('?')
                .first()
            )
            verse_id = verse.id if verse else None
            cache.set(cache_key, verse_id, timeout=60 * 60 * 24)
        verse = Verse.objects.filter(id=verse_id).first() if verse_id else None
        return self._build_verse_data(verse, category=category)

    # Devuelve el versÃ­culo asignado para estudio (placeholder)
    def get_study_verse_data(self):
        return self.get_static_verse_data()

    def get_verse_data(self, category=None):
        if self.experience_type == 'STATIC':
            return self.get_static_verse_data()
        if self.experience_type == 'DAILY':
            return self.get_daily_verse_data()
        if self.experience_type == 'CATEGORY':
            return self.get_category_verse_data(category)
        if self.experience_type == 'STUDY':
            return self.get_study_verse_data()
        return None


class NFCScan(models.Model):
    nfc_device = models.ForeignKey(NFCDevice, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)
    # opcional: podrÃ­as guardar IP, user_agent, etc.

    def __str__(self):
        return f"{self.nfc_device.public_uid} @ {self.scanned_at}"
