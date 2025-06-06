# church/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Event(models.Model):
    EVENT_CATEGORIES = [
        ("service", "Church Service"),
        ("meeting", "Meeting"),
        ("outreach", "Outreach"),
        ("conference", "Conference"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=EVENT_CATEGORIES, default="service"
    )
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.title} - {self.date}"


class Sermon(models.Model):
    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    topic = models.CharField(max_length=100)
    bible_verse = models.CharField(max_length=100, blank=True)
    audio_file = models.FileField(upload_to="sermons/audio/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    notes = models.FileField(upload_to="sermons/notes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} by {self.preacher}"
