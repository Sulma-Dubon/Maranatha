from django.db import models

class BibleVersion(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    license_type = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.abbreviation

class Book(models.Model):
    name = models.CharField(max_length=50)
    testament = models.CharField(max_length=10, choices=[('OT','Antiguo'), ('NT','Nuevo')])

    def __str__(self):
        return self.name

class VerseCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Verse(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chapter = models.PositiveIntegerField()
    verse_start = models.PositiveIntegerField()
    verse_end = models.PositiveIntegerField(null=True, blank=True)
    text = models.TextField()
    version = models.ForeignKey(BibleVersion, on_delete=models.PROTECT)
    categories = models.ManyToManyField(VerseCategory, blank=True)

    def __str__(self):
        return f"{self.book.name} {self.chapter}:{self.verse_start}"


