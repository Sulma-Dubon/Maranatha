from django.db import models

EXPERIENCE_CHOICES = [
    ('DAILY', 'Versículo diario'),
    ('CATEGORY', 'Por categoría'),
    ('STATIC', 'Versículo estático'),
    ('STUDY', 'Estudio editable'),
]

class NFCDevice(models.Model):
    public_uid = models.CharField(max_length=100, unique=True)
    experience_type = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.public_uid} ({self.experience_type})"

class NFCScan(models.Model):
    nfc_device = models.ForeignKey(NFCDevice, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)
    # opcional: podrías guardar IP, user_agent, etc.

    def __str__(self):
        return f"{self.nfc_device.public_uid} @ {self.scanned_at}"
