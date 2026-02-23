from django.core.management.base import BaseCommand

from content.models import BibleVersion, VerseCategory
from social.models import FeedPost


class Command(BaseCommand):
    help = "Create sample FeedPost rows for social feed preview."

    def handle(self, *args, **options):
        version = (
            BibleVersion.objects.filter(abbreviation="RVR1909").first()
            or BibleVersion.objects.filter(is_active=True).first()
        )
        amor = VerseCategory.objects.filter(slug="amor").first()
        fe = VerseCategory.objects.filter(slug="fe").first()
        general = VerseCategory.objects.filter(slug="general").first()

        samples = [
            {
                "title": "Reflexion del dia",
                "body": "Empieza con una oracion corta y comparte esperanza.",
                "category": amor or general,
                "version": version,
            },
            {
                "title": "Versiculo para hoy",
                "body": "Repite el versiculo en voz alta y meditalo dos minutos.",
                "category": fe or general,
                "version": version,
            },
            {
                "title": "Reto semanal",
                "body": "Escribe una accion concreta para vivir este mensaje.",
                "category": general,
                "version": version,
            },
            {
                "title": "Oracion guiada",
                "body": "Gracias por este dia, dame sabiduria y paz para avanzar.",
                "category": general,
                "version": version,
            },
            {
                "title": "Comparte esperanza",
                "body": "Envia este versiculo a alguien que necesite animo hoy.",
                "category": amor or general,
                "version": version,
            },
        ]

        created = 0
        for item in samples:
            _, was_created = FeedPost.objects.get_or_create(
                title=item["title"],
                defaults={
                    "body": item["body"],
                    "category": item["category"],
                    "version": item["version"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Feed posts seeded. created={created}"))
