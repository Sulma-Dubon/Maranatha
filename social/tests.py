from rest_framework.test import APITestCase

from content.models import BibleVersion, Book, Verse, VerseCategory
from experiences.models import ExperienceConfig
from nfc.models import NFCDevice
from social.models import FeedPost


class FeedViewTests(APITestCase):
    def setUp(self):
        self.version = BibleVersion.objects.create(name="Reina Valera 1909", abbreviation="RVR1909")
        self.other_version = BibleVersion.objects.create(name="King James", abbreviation="KJV")
        self.category = VerseCategory.objects.create(name="Amor", slug="amor")
        self.other_category = VerseCategory.objects.create(name="Fe", slug="fe")
        book = Book.objects.create(name="Juan", testament="NT")
        self.verse = Verse.objects.create(
            book=book,
            chapter=3,
            verse_start=16,
            verse_end=16,
            text="Texto",
            version=self.version,
        )
        self.verse.categories.add(self.category)

        self.nfc = NFCDevice.objects.create(public_uid="FEED123", experience_type="CATEGORY")
        ExperienceConfig.objects.create(
            nfc_device=self.nfc,
            category=self.category,
            version=self.version,
        )

        self.matching_post = FeedPost.objects.create(
            title="Post amor",
            body="Contenido",
            category=self.category,
            version=self.version,
            verse=self.verse,
        )
        self.global_post = FeedPost.objects.create(
            title="Global",
            body="Sin filtros",
        )
        FeedPost.objects.create(
            title="Otro contexto",
            body="No deberia salir",
            category=self.other_category,
            version=self.other_version,
        )

    def test_feed_filters_by_nfc_context(self):
        response = self.client.get("/api/feed/", {"public_uid": self.nfc.public_uid})
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data]
        self.assertIn(self.matching_post.title, titles)
        self.assertIn(self.global_post.title, titles)
        self.assertNotIn("Otro contexto", titles)
