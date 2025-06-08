from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

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
    category = models.CharField(
        max_length=20, choices=EVENT_CATEGORIES, default="service"
    )
    image = models.ImageField(
        upload_to="events/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Upload an image for this event",
    )
    is_trending = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attendees (leave blank for no limit)",
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time"]
        verbose_name = "Church Event"
        verbose_name_plural = "Church Events"
        indexes = [
            models.Index(fields=["date", "time"]),
            models.Index(fields=["is_trending"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%b %d, %Y')}"
    
    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%b %d, %Y')}"

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"pk": self.pk})



    def get_start_datetime(self):
        if self.date and self.time:
            naive = datetime.combine(self.date, self.time)
            # Convert naive to aware
            aware = timezone.make_aware(naive)
            return aware
        return None


    def get_end_datetime(self):
        if self.date and self.end_time:
            naive = datetime.combine(self.date, self.end_time)
            aware = timezone.make_aware(naive)
            return aware
        return None

    @property
    def get_status(self):
        now = timezone.now()
        start = self.get_start_datetime()
        end = self.get_end_datetime()

        if not start:
            return "unspecified"
        if end and now > end:
            return "ended"
        elif now < start:
            return "upcoming"
        elif end and start <= now <= end:
            return "happening"
        return "ongoing"

    def available_seats(self):
        if not self.max_attendees:
            return "Unlimited"
        registered = (
            self.rsvps.filter(attending=True).aggregate(
                total=models.Sum(models.F("guests") + 1)
            )["total"]
            or 0
        )
        return max(0, self.max_attendees - registered)


class EventRSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_rsvps")
    attending = models.BooleanField(default=True)
    guests = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10)],
        help_text="Number of additional guests",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("event", "user")
        verbose_name = "Event RSVP"
        verbose_name_plural = "Event RSVPs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.event.title}"

    def total_attendees(self):
        return self.guests + 1 if self.attending else 0

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"], name="unique_event_user_rsvp"
            )
        ]


class Sermon(models.Model):
    SERMON_TYPES = [
        ("sunday", "Sunday Service"),
        ("bible", "Bible Study"),
        ("special", "Special Service"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=100)
    date = models.DateField()
    sermon_type = models.CharField(
        max_length=20, choices=SERMON_TYPES, default="sunday"
    )
    topic = models.CharField(max_length=100, blank=True)
    bible_verse = models.CharField(max_length=100, blank=True)
    scripture_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    audio_file = models.FileField(
        upload_to="sermons/audio/%Y/%m/",
        blank=True,
        null=True,
        help_text="Upload audio file of the sermon",
    )
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo link")
    slides = models.FileField(
        upload_to="sermons/slides/%Y/%m/",
        blank=True,
        null=True,
        help_text="PDF or PowerPoint slides",
    )
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="sermons"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Church Sermon"
        verbose_name_plural = "Church Sermons"
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["preacher"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.preacher} ({self.date})"

    def get_absolute_url(self):
        return reverse("sermon-detail", kwargs={"pk": self.pk})

    def duration_in_minutes(self):
        # You would need to add a duration field or calculate from audio/video
        return None
