from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.utils import timezone
from nfc.models import NFCDevice, NFCScan
from content.models import Verse, VerseCategory, BibleVersion
from .models import ExperienceConfig, StudyVerseAssignment, BackgroundImage
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
        data, error = _get_experience_payload(public_uid, study_only=True)
        if error:
            return Response({"detail": error[0]}, status=error[1])
        return Response(data, status=status.HTTP_200_OK)


class CategoryTodayView(APIView):
    def get(self, request, category_slug, version_abbr=None):
        if not version_abbr:
            version_abbr = request.query_params.get("version")
        data, error = _get_today_category_payload(category_slug, version_abbr=version_abbr)
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


class VersionsView(APIView):
    def get(self, request):
        qs = BibleVersion.objects.filter(is_active=True).order_by('abbreviation')
        data = [
            {"id": v.id, "name": v.name, "abbreviation": v.abbreviation}
            for v in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class CategoriesView(APIView):
    def get(self, request):
        qs = VerseCategory.objects.filter(is_active=True).order_by('name')
        data = [
            {"id": c.id, "name": c.name, "slug": c.slug, "description": c.description}
            for c in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class ExperienceTypesView(APIView):
    def get(self, request):
        data = [{"value": key, "label": label} for key, label in NFCDevice.EXPERIENCE_CHOICES]
        return Response(data, status=status.HTTP_200_OK)


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
        version_abbr = request.data.get('version')
        category_slug = request.data.get('category')
        if not verse_id:
            return Response({"detail": "verse_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        if not version_abbr:
            return Response({"detail": "version es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        if not category_slug:
            return Response({"detail": "category es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        version = BibleVersion.objects.filter(abbreviation=version_abbr, is_active=True).first()
        if not version:
            return Response({"detail": "Version no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        category = VerseCategory.objects.filter(slug=category_slug, is_active=True).first()
        if not category:
            return Response({"detail": "Categoria no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        verse = Verse.objects.filter(id=verse_id).select_related('book', 'version').first()
        if not verse:
            return Response({"detail": "Versiculo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if verse.version_id != version.id:
            return Response(
                {"detail": "El versiculo no pertenece a la version seleccionada"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not verse.categories.filter(id=category.id).exists():
            return Response(
                {"detail": "El versiculo no pertenece a la categoria seleccionada"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        config.version = version
        config.category = category
        config.save(update_fields=["version", "category"])
        StudyVerseAssignment.objects.get_or_create(config=config, verse=verse)
        verse_data = nfc_device._build_verse_data(verse)
        return Response({"detail": "Asignado", "verse_data": verse_data}, status=status.HTTP_201_CREATED)


def experience_page(request, public_uid):
    data, error = _get_experience_payload(public_uid, study_only=True)
    theme = (request.GET.get("theme") or "a").lower()
    if theme not in {"a", "b"}:
        theme = "a"
    context = {"data": data, "error": None}
    context["theme"] = theme
    context["theme_class"] = f"theme-{theme}"
    context["base_path"] = f"/nfc/{public_uid}/"
    context["background_image_url"] = _pick_background_image_url(data)
    if error:
        context["error"] = error[0]
    return render(request, "experiences/nfc_public.html", context)


def today_category_page(request, category_slug, version_abbr=None):
    if not version_abbr:
        version_abbr = request.GET.get("version")
    data, error = _get_today_category_payload(category_slug, version_abbr=version_abbr)
    theme = (request.GET.get("theme") or "a").lower()
    if theme not in {"a", "b"}:
        theme = "a"
    context = {"data": data, "error": None}
    context["theme"] = theme
    context["theme_class"] = f"theme-{theme}"
    context["base_path"] = f"/hoy/{category_slug}/"
    if version_abbr:
        context["base_path"] = f"/hoy/{category_slug}/{version_abbr}/"
    context["background_image_url"] = _pick_background_image_url(data)
    if error:
        context["error"] = error[0]
    return render(request, "experiences/nfc_public.html", context)


def study_page(request, public_uid):
    data, error = _get_experience_payload(public_uid, study_only=True)
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
    active_versions = BibleVersion.objects.filter(is_active=True).order_by("abbreviation")
    active_categories = VerseCategory.objects.filter(is_active=True).order_by("name")
    selected_version = request.GET.get("version") or (config.version.abbreviation if config and config.version else None)
    selected_category = request.GET.get("category") or (config.category.slug if config and config.category else None)
    if request.method == "POST":
        selected_version = request.POST.get("version") or selected_version
        selected_category = request.POST.get("category") or selected_category

    verses = Verse.objects.none()
    if selected_version and selected_category:
        verses = (
            Verse.objects.filter(categories__slug=selected_category, version__abbreviation=selected_version)
            .select_related('book', 'version')
            .order_by('book__name', 'chapter', 'verse_start')
        )

    selected_id = None
    saved = False
    if request.method == "POST":
        verse_id = request.POST.get("verse_id")
        if verse_id:
            verse = Verse.objects.filter(id=verse_id).first()
            version = BibleVersion.objects.filter(abbreviation=selected_version, is_active=True).first()
            category = VerseCategory.objects.filter(slug=selected_category, is_active=True).first()
            if (
                verse
                and version
                and category
                and verse.version_id == version.id
                and verse.categories.filter(id=category.id).exists()
            ):
                config.version = version
                config.category = category
                config.save(update_fields=["version", "category"])
                StudyVerseAssignment.objects.get_or_create(config=config, verse=verse)
                data["verse_data"] = nfc_device._build_verse_data(verse)
                selected_id = verse.id
                saved = True
                return redirect(f"/nfc/{public_uid}/")

    context = {
        "data": data,
        "error": None,
        "verses": verses,
        "versions": active_versions,
        "categories": active_categories,
        "selected_version": selected_version,
        "selected_category": selected_category,
        "selected_id": selected_id,
        "saved": saved,
    }
    return render(request, "experiences/nfc_study.html", context)


def _get_today_category_payload(category_slug, version_abbr=None):
    category = VerseCategory.objects.filter(slug=category_slug, is_active=True).first()
    if not category:
        return None, ("Categoria no encontrada", status.HTTP_404_NOT_FOUND)

    if not version_abbr:
        return None, ("Debes indicar version", status.HTTP_400_BAD_REQUEST)
    version = BibleVersion.objects.filter(abbreviation=version_abbr, is_active=True).first()
    if not version:
        return None, ("Version no encontrada", status.HTTP_404_NOT_FOUND)

    day_key = timezone.localdate().isoformat()
    cache_key = f"daily_verse:{category.id}:{version.abbreviation}:{day_key}"
    verse_id = cache.get(cache_key)
    if verse_id is None:
        verse = (
            Verse.objects.filter(version=version, categories=category)
            .order_by("?")
            .first()
        )
        verse_id = verse.id if verse else None
        cache.set(cache_key, verse_id, timeout=60 * 60 * 24)
    verse = Verse.objects.filter(id=verse_id).select_related("book").first() if verse_id else None
    if not verse:
        return None, ("No hay versiculos para esta categoria/version", status.HTTP_404_NOT_FOUND)

    data = {
        "public_uid": None,
        "experience_type": "CATEGORY_PUBLIC",
        "verse_data": {
            "book": verse.book.name,
            "chapter": verse.chapter,
            "verse_start": verse.verse_start,
            "verse_end": verse.verse_end,
            "text": verse.text,
            "category": category.name,
        },
        "category_slug": category.slug,
        "version": version.abbreviation,
    }
    return data, None


def _get_experience_payload(public_uid, study_only=False):
    try:
        nfc_device = NFCDevice.objects.get(public_uid=public_uid, is_active=True)
    except NFCDevice.DoesNotExist:
        return None, ("NFC no encontrado", status.HTTP_404_NOT_FOUND)

    if study_only and nfc_device.experience_type != "STUDY":
        return None, ("Este NFC ahora solo funciona para modo STUDY", status.HTTP_400_BAD_REQUEST)

    if settings.ENABLE_NFC_SCAN_LOGS:
        NFCScan.objects.create(nfc_device=nfc_device)

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
        "category_slug": config.category.slug if config and config.category else None,
        "version": version_abbr,
    }
    return data, None


def _pick_background_image_url(data):
    if not data:
        return None

    category_slug = data.get("category_slug")
    version_abbr = data.get("version")

    category = VerseCategory.objects.filter(slug=category_slug).first() if category_slug else None
    version = BibleVersion.objects.filter(abbreviation=version_abbr).first() if version_abbr else None

    # Priority: exact scope -> category only -> version only -> global
    candidates = None
    if category and version:
        candidates = BackgroundImage.objects.filter(is_active=True, category=category, version=version)
    if not candidates or not candidates.exists():
        if category:
            candidates = BackgroundImage.objects.filter(is_active=True, category=category, version__isnull=True)
    if not candidates or not candidates.exists():
        if version:
            candidates = BackgroundImage.objects.filter(is_active=True, category__isnull=True, version=version)
    if not candidates or not candidates.exists():
        candidates = BackgroundImage.objects.filter(is_active=True, category__isnull=True, version__isnull=True)

    image = candidates.order_by("?").first() if candidates else None
    return image.image.url if image and image.image else None
