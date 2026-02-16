from datetime import date, timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from content.models import BibleVersion, Book, Verse, VerseCategory
from nfc.models import NFCDevice, NFCScan


class DailyVerseSelectionTests(TestCase):
    def setUp(self):
        self.version = BibleVersion.objects.create(name="Reina Valera 1909", abbreviation="RVR1909")
        self.book = Book.objects.create(name="Juan", testament="NT")
        self.nfc = NFCDevice.objects.create(public_uid="TEST-DAILY", experience_type="DAILY")

        # Multiple verses are required to validate day-to-day rotation.
        self.verses = [
            Verse.objects.create(
                book=self.book,
                chapter=3,
                verse_start=i + 1,
                verse_end=i + 1,
                text=f"Texto {i + 1}",
                version=self.version,
            )
            for i in range(3)
        ]

    def test_daily_changes_when_date_changes(self):
        day_1 = date(2026, 2, 10)
        day_2 = day_1 + timedelta(days=1)

        with patch("nfc.models.timezone.localdate", return_value=day_1):
            verse_day_1 = self.nfc.get_daily_verse_data(version=self.version.abbreviation)

        with patch("nfc.models.timezone.localdate", return_value=day_2):
            verse_day_2 = self.nfc.get_daily_verse_data(version=self.version.abbreviation)

        self.assertIsNotNone(verse_day_1)
        self.assertIsNotNone(verse_day_2)
        self.assertNotEqual(
            (verse_day_1["chapter"], verse_day_1["verse_start"]),
            (verse_day_2["chapter"], verse_day_2["verse_start"]),
        )


class CategoryDailyCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        self.version = BibleVersion.objects.create(name="Reina Valera 1909", abbreviation="RVR1909")
        self.book = Book.objects.create(name="Salmos", testament="OT")
        self.category = VerseCategory.objects.create(name="Amor", slug="amor")
        self.nfc = NFCDevice.objects.create(public_uid="TEST-CATEGORY", experience_type="CATEGORY")

        self.verse_a = Verse.objects.create(
            book=self.book,
            chapter=1,
            verse_start=1,
            verse_end=1,
            text="Texto A",
            version=self.version,
        )
        self.verse_b = Verse.objects.create(
            book=self.book,
            chapter=1,
            verse_start=2,
            verse_end=2,
            text="Texto B",
            version=self.version,
        )
        self.verse_a.categories.add(self.category)
        self.verse_b.categories.add(self.category)

    def test_category_is_stable_within_same_day(self):
        today = date(2026, 2, 10)

        with patch("nfc.models.timezone.localdate", return_value=today):
            first = self.nfc.get_category_verse_data(category=self.category, version=self.version.abbreviation)
        with patch("nfc.models.timezone.localdate", return_value=today):
            second = self.nfc.get_category_verse_data(category=self.category, version=self.version.abbreviation)

        self.assertIsNotNone(first)
        self.assertEqual(
            (first["chapter"], first["verse_start"]),
            (second["chapter"], second["verse_start"]),
        )

    def test_category_uses_a_different_cache_key_next_day(self):
        day_1 = date(2026, 2, 10)
        day_2 = day_1 + timedelta(days=1)
        cache_key_day_1 = f"daily_verse:{self.category.id}:{self.version.abbreviation}:{day_1.isoformat()}"

        # Force an invalid verse id only for day 1 to verify day 2 uses another key.
        cache.set(cache_key_day_1, -1, timeout=60 * 60 * 24)

        with patch("nfc.models.timezone.localdate", return_value=day_2):
            day_2_data = self.nfc.get_category_verse_data(category=self.category, version=self.version.abbreviation)

        self.assertIsNotNone(day_2_data)


class ScanLoggingFlagTests(TestCase):
    def setUp(self):
        self.nfc = NFCDevice.objects.create(public_uid="TEST-SCAN-FLAG", experience_type="DAILY")

    @override_settings(ENABLE_NFC_SCAN_LOGS=True)
    def test_public_nfc_endpoint_logs_scan_when_enabled(self):
        response = self.client.get(f"/api/nfc/{self.nfc.public_uid}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(NFCScan.objects.filter(nfc_device=self.nfc).count(), 1)

    @override_settings(ENABLE_NFC_SCAN_LOGS=False)
    def test_public_nfc_endpoint_does_not_log_scan_when_disabled(self):
        response = self.client.get(f"/api/nfc/{self.nfc.public_uid}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(NFCScan.objects.filter(nfc_device=self.nfc).count(), 0)
