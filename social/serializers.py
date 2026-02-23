from rest_framework import serializers

from .models import FeedPost


class FeedPostSerializer(serializers.ModelSerializer):
    verse_ref = serializers.SerializerMethodField()
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    version_abbreviation = serializers.CharField(source="version.abbreviation", read_only=True)

    class Meta:
        model = FeedPost
        fields = [
            "id",
            "title",
            "body",
            "verse_ref",
            "category_slug",
            "version_abbreviation",
            "published_at",
        ]

    def get_verse_ref(self, obj):
        if not obj.verse:
            return None
        return f"{obj.verse.book.name} {obj.verse.chapter}:{obj.verse.verse_start}"
