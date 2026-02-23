from django.contrib import admin

from .models import FeedPost


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category", "version", "is_active", "published_at"]
    list_filter = ["is_active", "category", "version"]
    search_fields = ["title", "body"]
