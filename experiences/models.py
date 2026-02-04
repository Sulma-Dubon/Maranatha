from django.db import models
from nfc.models import NFCDevice
from content.models import Verse, VerseCategory, BibleVersion

class ExperienceConfig(models.Model):
    nfc_device = models.OneToOneField(NFCDevice, on_delete=models.CASCADE)
    category = models.ForeignKey(VerseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.ForeignKey(BibleVersion, on_delete=models.PROTECT)
    is_editable = models.BooleanField(default=False)  # para estudio editable

    def __str__(self):
        return f"Config {self.nfc_device.public_uid}"

class StudyVerseAssignment(models.Model):
    nfc_device = models.OneToOneField(NFCDevice, on_delete=models.CASCADE)
    verse = models.ForeignKey(Verse, on_delete=models.PROTECT)
    version = models.ForeignKey(BibleVersion, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nfc_device.public_uid} → {self.verse}"
