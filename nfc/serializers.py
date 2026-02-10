
from rest_framework import serializers
from .models import NFCDevice

class PublicNFCSerializer(serializers.ModelSerializer):
    verse_data = serializers.SerializerMethodField()

    class Meta:
        model = NFCDevice
        fields = ['public_uid', 'experience_type', 'verse_data']

    def get_verse_data(self, obj):
        if obj.experience_type == 'STATIC':
            return obj.get_static_verse_data()
        elif obj.experience_type == 'DAILY':
            return obj.get_daily_verse_data()
        # CATEGORY y STUDY se implementarán más adelante
        return None
