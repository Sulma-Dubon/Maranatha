from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from nfc.models import NFCDevice
from content.models import Verse
from content.models import VerseCategory
from .models import ExperienceConfig, StudyVerseAssignment
from .serializers import VerseSerializer


class ExperienceView(APIView):
    """
    Devuelve el contenido segun la experiencia del NFCDevice:
    - STATIC: versiculo fijo
    - DAILY: versiculo diario deterministico
    - CATEGORY: por categoria
    - STUDY: editable por el usuario
    """

    def get(self, request, public_uid):
        data, error = _get_experience_payload(public_uid)
        if error:
            return Response({"detail": error[0]}, status=error[1])
        return Response(data, status=status.HTTP_200_OK)


class VerseListView(APIView):
    def get(self, request):
        qs = Verse.objects.select_related('book', 'version').all()

        version = request.query_params.get('version')
        if version:
            qs = qs.filter(version__abbreviation=version)

        category_slug = request.query_params.get('category')
        if category_slug:
            qs = qs.filter(categories__slug=category_slug)

        book_id = request.query_params.get('book_id')
        if book_id:
            qs = qs.filter(book_id=book_id)

        chapter = request.query_params.get('chapter')
        if chapter:
            qs = qs.filter(chapter=chapter)

        try:
            limit = int(request.query_params.get('limit', 50))
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 200))
        qs = qs.order_by('id')[:limit]

        serializer = VerseSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudyVerseAddView(APIView):
    def post(self, request, public_uid):
        try:
            nfc_device = NFCDevice.objects.get(public_uid=public_uid, is_active=True)
        except NFCDevice.DoesNotExist:
            return Response({"detail": "NFC no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if nfc_device.experience_type != 'STUDY':
            return Response({"detail": "El NFC no esta en modo estudio"}, status=status.HTTP_400_BAD_REQUEST)

        config = ExperienceConfig.objects.filter(nfc_device=nfc_device).first()
        if not config:
            return Response({"detail": "Config no encontrada para este NFC"}, status=status.HTTP_404_NOT_FOUND)

        verse_id = request.data.get('verse_id')
        if not verse_id:
            return Response({"detail": "verse_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        verse = Verse.objects.filter(id=verse_id).select_related('book', 'version').first()
        if not verse:
            return Response({"detail": "Versiculo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            general_category = VerseCategory.objects.get(slug='general')
        except VerseCategory.DoesNotExist:
            return Response({"detail": "Categoria general no existe"}, status=status.HTTP_400_BAD_REQUEST)

        if not verse.categories.filter(id=general_category.id).exists():
            return Response(
                {"detail": "El versiculo no pertenece a la categoria general"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        StudyVerseAssignment.objects.get_or_create(config=config, verse=verse)
        verse_data = nfc_device._build_verse_data(verse)
        return Response({"detail": "Asignado", "verse_data": verse_data}, status=status.HTTP_201_CREATED)


def experience_page(request, public_uid):
    data, error = _get_experience_payload(public_uid)
    context = {"data": data, "error": None}
    if error:
        context["error"] = error[0]
    return render(request, "experiences/nfc_public.html", context)


def study_page(request, public_uid):
    data, error = _get_experience_payload(public_uid)
    if error:
        return render(request, "experiences/nfc_study.html", {"error": error[0], "data": None})

    if data["experience_type"] != "STUDY":
        return render(
            request,
            "experiences/nfc_study.html",
            {"error": "Este NFC no esta en modo estudio", "data": data},
        )

    nfc_device = NFCDevice.objects.get(public_uid=public_uid)
    config = (
        ExperienceConfig.objects.filter(nfc_device=nfc_device)
        .select_related('category', 'version')
        .first()
    )
    version_abbr = config.version.abbreviation if config and config.version else None
    general_category = VerseCategory.objects.filter(slug='general').first()

    verses = Verse.objects.none()
    if version_abbr and general_category:
        verses = (
            Verse.objects.filter(categories=general_category, version__abbreviation=version_abbr)
            .select_related('book', 'version')
            .order_by('book__name', 'chapter', 'verse_start')
        )

    selected_id = None
    saved = False
    if request.method == "POST":
        verse_id = request.POST.get("verse_id")
        if verse_id:
            verse = Verse.objects.filter(id=verse_id).first()
            if verse and general_category and verse.categories.filter(id=general_category.id).exists():
                StudyVerseAssignment.objects.get_or_create(config=config, verse=verse)
                data["verse_data"] = nfc_device._build_verse_data(verse)
                selected_id = verse.id
                saved = True
                return redirect(f"/nfc/{public_uid}/")

    context = {
        "data": data,
        "error": None,
        "verses": verses,
        "selected_id": selected_id,
        "saved": saved,
    }
    return render(request, "experiences/nfc_study.html", context)


def _get_experience_payload(public_uid):
    try:
        nfc_device = NFCDevice.objects.get(public_uid=public_uid, is_active=True)
    except NFCDevice.DoesNotExist:
        return None, ("NFC no encontrado", status.HTTP_404_NOT_FOUND)

    config = (
        ExperienceConfig.objects.filter(nfc_device=nfc_device)
        .select_related('category', 'version', 'static_verse')
        .first()
    )
    version_abbr = config.version.abbreviation if config and config.version else None
    if not version_abbr:
        return None, ("Config sin version seleccionada", status.HTTP_400_BAD_REQUEST)

    verse_data = None
    if nfc_device.experience_type == 'STATIC':
        if config and config.static_verse:
            verse_data = nfc_device.get_static_verse_data(verse=config.static_verse)
        else:
            verse_data = nfc_device.get_static_verse_data(version=version_abbr)
    elif nfc_device.experience_type == 'DAILY':
        verse_data = nfc_device.get_daily_verse_data(version=version_abbr)
    elif nfc_device.experience_type == 'CATEGORY':
        category = config.category if config else None
        verse_data = nfc_device.get_category_verse_data(category=category, version=version_abbr)
    elif nfc_device.experience_type == 'STUDY':
        if config:
            assignment = (
                StudyVerseAssignment.objects.filter(config=config)
                .select_related('verse', 'verse__book', 'verse__version')
                .order_by('-updated_at')
                .first()
            )
            verse_data = nfc_device._build_verse_data(assignment.verse) if assignment else None
        else:
            verse_data = None

    data = {
        "public_uid": nfc_device.public_uid,
        "experience_type": nfc_device.experience_type,
        "verse_data": verse_data,
    }
    return data, None
