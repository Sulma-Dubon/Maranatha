from django.contrib import admin
from .models import ExperienceConfig, StudyVerseAssignment, BackgroundImage


@admin.register(ExperienceConfig)
class ExperienceConfigAdmin(admin.ModelAdmin):
    list_display = ['nfc_device', 'category', 'version', 'static_verse', 'is_editable']
    list_filter = ['category', 'version', 'is_editable']
    search_fields = ['nfc_device__public_uid']


@admin.register(StudyVerseAssignment)
class StudyVerseAssignmentAdmin(admin.ModelAdmin):
    list_display = ['config', 'verse', 'updated_at']
    list_filter = ['config']
    search_fields = ['config__nfc_device__public_uid']


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'version']
