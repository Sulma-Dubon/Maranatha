from django.db import models
from nfc.models import NFCDevice
from content.models import Verse, VerseCategory, BibleVersion


class ExperienceConfig(models.Model):
    nfc_device = models.OneToOneField(NFCDevice, on_delete=models.CASCADE)
    category = models.ForeignKey(VerseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.ForeignKey(BibleVersion, on_delete=models.PROTECT)
    static_verse = models.ForeignKey(Verse, null=True, blank=True, on_delete=models.SET_NULL)
    is_editable = models.BooleanField(default=False)  # estudio editable

    def __str__(self):
        return f"Config {self.nfc_device.public_uid}"


class StudyVerseAssignment(models.Model):
    config = models.ForeignKey(
        ExperienceConfig,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="study_verses",
    )
    verse = models.ForeignKey(Verse, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.config.nfc_device.public_uid} -> {self.verse}"


class BackgroundImage(models.Model):
    image = models.ImageField(upload_to="backgrounds/")
    category = models.ForeignKey(VerseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.ForeignKey(BibleVersion, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        scope = []
        if self.category:
            scope.append(self.category.slug)
        if self.version:
            scope.append(self.version.abbreviation)
        suffix = f" ({', '.join(scope)})" if scope else " (global)"
        return f"Background {self.id}{suffix}"
