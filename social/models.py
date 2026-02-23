from django.conf import settings
from django.db import models
from django.utils import timezone

from content.models import Verse, VerseCategory, BibleVersion


class FeedPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feed_posts",
    )
    title = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    verse = models.ForeignKey(Verse, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(VerseCategory, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.ForeignKey(BibleVersion, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title or f"Post {self.id}"
