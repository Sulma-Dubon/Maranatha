from django.contrib import admin
from .models import BibleVersion, Book, VerseCategory, Verse

admin.site.register(BibleVersion)
admin.site.register(Book)
admin.site.register(VerseCategory)
admin.site.register(Verse)

