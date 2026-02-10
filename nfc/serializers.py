from rest_framework import serializers
from .models import NFCDevice


class PublicNFCSerializer(serializers.ModelSerializer):
    verse_data = serializers.SerializerMethodField()

    class Meta:
        model = NFCDevice
        fields = ['public_uid', 'experience_type', 'verse_data']

    def get_verse_data(self, obj):
        return obj.get_verse_data()
