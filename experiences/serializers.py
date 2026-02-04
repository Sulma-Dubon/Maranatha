from rest_framework import serializers
from content.models import Verse

class VerseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verse
        fields = [
            'book',
            'chapter',
            'verse_number',
            'text'
        ]
