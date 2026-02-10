from rest_framework import serializers
from content.models import Verse


class VerseSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    version = serializers.StringRelatedField()

    class Meta:
        model = Verse
        fields = [
            'id',
            'book',
            'chapter',
            'verse_start',
            'verse_end',
            'text',
            'version',
        ]
