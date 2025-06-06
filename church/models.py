# church/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime

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
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES, default="service")
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_trending = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.title} - {self.date}"

    def get_start_datetime(self):
        return timezone.make_aware(datetime.combine(self.date, self.time))

    def get_end_datetime(self):
        if self.end_time:
            return timezone.make_aware(datetime.combine(self.date, self.end_time))
        return None

    def get_status(self):
        now = timezone.now()
        start = self.get_start_datetime()
        end = self.get_end_datetime()

        if end and now > end:
            return "ended"
        elif now < start:
            return "upcoming"
        elif end and start <= now <= end:
            return "happening"
        else:
            return "ongoing"

class EventRSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attending = models.BooleanField(default=True)
    guests = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = 'Event RSVP'
        verbose_name_plural = 'Event RSVPs'

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"