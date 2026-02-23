from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from experiences.models import ExperienceConfig
from nfc.models import NFCDevice

from .models import FeedPost
from .serializers import FeedPostSerializer


class FeedView(APIView):
    def get(self, request):
        qs = FeedPost.objects.filter(is_active=True).select_related("category", "version", "verse", "verse__book")
        public_uid = request.query_params.get("public_uid")
        limit = request.query_params.get("limit", 20)

        if public_uid:
            nfc = NFCDevice.objects.filter(public_uid=public_uid, is_active=True).first()
            if nfc:
                config = ExperienceConfig.objects.select_related("category", "version").filter(nfc_device=nfc).first()
                if config:
                    if config.category_id:
                        qs = qs.filter(Q(category_id=config.category_id) | Q(category__isnull=True))
                    if config.version_id:
                        qs = qs.filter(Q(version_id=config.version_id) | Q(version__isnull=True))

        try:
            limit = max(1, min(int(limit), 50))
        except ValueError:
            limit = 20

        serializer = FeedPostSerializer(qs[:limit], many=True)
        return Response(serializer.data)
