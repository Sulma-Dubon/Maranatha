from django.core.cache import cache
from django.test import TestCase

from content.models import BibleVersion, Book, Verse, VerseCategory
from experiences.models import ExperienceConfig
from nfc.models import NFCDevice


class CategoryTodayFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.version = BibleVersion.objects.create(name="Reina Valera 1909", abbreviation="RVR1909")
        self.category = VerseCategory.objects.create(name="Amor", slug="amor")
        book = Book.objects.create(name="Juan", testament="NT")
        verse = Verse.objects.create(
            book=book,
            chapter=3,
            verse_start=16,
            verse_end=16,
            text="Texto",
            version=self.version,
        )
        verse.categories.add(self.category)

    def test_today_category_endpoint_returns_verse(self):
        response = self.client.get(f"/api/today/{self.category.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["experience_type"], "CATEGORY_PUBLIC")
        self.assertEqual(response.json()["verse_data"]["category"], self.category.name)


class NfcStudyOnlyTests(TestCase):
    def setUp(self):
        version = BibleVersion.objects.create(name="Reina Valera 1909", abbreviation="RVR1909")
        category = VerseCategory.objects.create(name="General", slug="general")
        self.nfc_category = NFCDevice.objects.create(public_uid="NFC-CATEGORY", experience_type="CATEGORY")
        self.nfc_study = NFCDevice.objects.create(public_uid="NFC-STUDY", experience_type="STUDY")
        ExperienceConfig.objects.create(nfc_device=self.nfc_category, category=category, version=version)
        ExperienceConfig.objects.create(nfc_device=self.nfc_study, category=category, version=version)

    def test_nfc_endpoint_rejects_non_study(self):
        response = self.client.get(f"/api/nfc/{self.nfc_category.public_uid}/")
        self.assertEqual(response.status_code, 400)

    def test_nfc_endpoint_allows_study(self):
        response = self.client.get(f"/api/nfc/{self.nfc_study.public_uid}/")
        self.assertEqual(response.status_code, 200)
