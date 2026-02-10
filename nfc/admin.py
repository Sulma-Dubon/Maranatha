from django.contrib import admin
from .models import NFCDevice, NFCScan
from experiences.models import ExperienceConfig, StudyVerseAssignment


class StudyVerseInline(admin.TabularInline):
    model = StudyVerseAssignment
    extra = 0
    autocomplete_fields = ['verse']


class ExperienceConfigInline(admin.StackedInline):
    model = ExperienceConfig
    extra = 0
    show_change_link = True


@admin.register(NFCDevice)
class NFCDeviceAdmin(admin.ModelAdmin):
    list_display = ['public_uid', 'experience_type', 'user', 'is_active', 'created_at']
    list_filter = ['experience_type', 'is_active']
    search_fields = ['public_uid']
    inlines = [ExperienceConfigInline]


@admin.register(NFCScan)
class NFCScanAdmin(admin.ModelAdmin):
    list_display = ['nfc_device', 'scanned_at']
