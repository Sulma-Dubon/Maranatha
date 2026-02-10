import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from content.models import BibleVersion, Book, Verse, VerseCategory


class Command(BaseCommand):
    help = "Import verses from a CSV file (semicolon-separated)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="verses.csv",
            help="Path to verses CSV (default: verses.csv)",
        )
        parser.add_argument(
            "--assign-general",
            action="store_true",
            help="Assign all imported verses to the 'general' category.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        created = 0
        updated = 0

        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                version_abbr = row.get("version")
                book_name = row.get("book")
                chapter = int(row.get("chapter") or 0)
                verse_start = int(row.get("verse_start") or 0)
                verse_end = int(row.get("verse_end") or verse_start)
                text = row.get("text") or ""
                category_slug = row.get("category") or ""

                if not version_abbr or not book_name or not chapter or not verse_start or not text:
                    continue

                version, _ = BibleVersion.objects.get_or_create(
                    abbreviation=version_abbr,
                    defaults={"name": version_abbr},
                )
                book, _ = Book.objects.get_or_create(
                    name=book_name,
                    defaults={"testament": "OT"},
                )

                verse, is_created = Verse.objects.get_or_create(
                    book=book,
                    chapter=chapter,
                    verse_start=verse_start,
                    defaults={
                        "verse_end": verse_end,
                        "text": text,
                        "version": version,
                    },
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
                    verse.verse_end = verse_end
                    verse.text = text
                    verse.version = version
                    verse.save()

                if category_slug:
                    category, _ = VerseCategory.objects.get_or_create(
                        slug=category_slug,
                        defaults={"name": category_slug.capitalize()},
                    )
                    verse.categories.add(category)

        if options["assign_general"]:
            general, _ = VerseCategory.objects.get_or_create(
                slug="general",
                defaults={"name": "General", "description": "Categoria general"},
            )
            general.verse_set.add(*Verse.objects.all())

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. created={created} updated={updated}"
            )
        )
