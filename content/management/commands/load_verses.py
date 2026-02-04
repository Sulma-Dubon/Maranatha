import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from content.models import BibleVersion, Book, Verse, VerseCategory


class Command(BaseCommand):
    help = "Carga versículos bíblicos desde un CSV delimitado por ';'"

    def handle(self, *args, **options):
        csv_path = "verses.csv"  # Ajusta la ruta si es necesario
        created_count = 0

        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')  # <- punto y coma
            for row_number, row in enumerate(reader, start=2):
                try:
                    # 🔹 Limpieza defensiva
                    version_abbr = (row.get("version") or "").strip()
                    book_name = (row.get("book") or "").strip()
                    chapter = int(row.get("chapter") or 0)
                    verse_start = int(row.get("verse_start") or 0)
                    verse_end = int(row.get("verse_end") or verse_start)
                    text = (row.get("text") or "").strip()
                    category_name = (row.get("category") or "").strip()

                    # 🔸 Validaciones mínimas
                    if not version_abbr or not book_name or not chapter or not verse_start or not text:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Fila {row_number} ignorada (datos incompletos)"
                            )
                        )
                        continue

                    # 1️⃣ BibleVersion
                    version, _ = BibleVersion.objects.get_or_create(
                        abbreviation=version_abbr,
                        defaults={"name": version_abbr}
                    )

                    # 2️⃣ Libro
                    book, _ = Book.objects.get_or_create(name=book_name)

                    # 3️⃣ Categoría (opcional)
                    category = None
                    if category_name:
                        category_slug = slugify(category_name)
                        category, _ = VerseCategory.objects.get_or_create(
                            slug=category_slug,
                            defaults={"name": category_name}
                        )

                    # 4️⃣ Versículo (evita duplicados)
                    verse, created = Verse.objects.get_or_create(
                        version=version,
                        book=book,
                        chapter=chapter,
                        verse_start=verse_start,
                        defaults={
                            "verse_end": verse_end,
                            "text": text,
                        }
                    )

                    # Asignar categoría después si existe
                    if category:
                        verse.categories.add(category)

                    # Actualiza si ya existe pero estaba incompleto
                    if not created:
                        updated = False
                        if not verse.text:
                            verse.text = text
                            updated = True
                        if category and not verse.categories.exists():
                            verse.categories.add(category)
                            updated = True
                        if verse.verse_end != verse_end:
                            verse.verse_end = verse_end
                            updated = True
                        if updated:
                            verse.save()

                    if created:
                        created_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error en fila {row_number}: {e}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso finalizado. Versículos creados: {created_count}"
            )
        )
