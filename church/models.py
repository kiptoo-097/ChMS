from django.db import models
from django.utils.text import slugify
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

    from django.utils import timezone


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


# models.py (add these to your existing models)
class SermonSeries(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='sermon_series/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Sermon Series"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sermon_series_detail', kwargs={'pk': self.pk})


class Sermon(models.Model):
    SERMON_TYPES = [
        ('sunday', 'Sunday Service'),
        ('bible_study', 'Bible Study'),
        ('special', 'Special Service'),
        ('conference', 'Conference'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=200)
    sermon_type = models.CharField(max_length=20, choices=SERMON_TYPES, default='sunday')
    series = models.ForeignKey(SermonSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name='sermons')
    date_preached = models.DateField()
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    sermon_notes = models.TextField(blank=True)
    bible_passage = models.CharField(max_length=100, blank=True)
    thumbnail = models.ImageField(upload_to='sermons/thumbnails/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_preached']
        verbose_name_plural = "Sermons"
        indexes = [
            models.Index(fields=['-date_preached']),
            models.Index(fields=['preacher']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"{self.title} - {self.preacher} ({self.date_preached.strftime('%b %d, %Y')})"

    def get_absolute_url(self):
        return reverse('sermon_detail', kwargs={'pk': self.pk})

    @property
    def is_upcoming(self):
        return self.date_preached > timezone.now().date()


class UpcomingSermon(models.Model):
    sermon = models.OneToOneField(Sermon, on_delete=models.CASCADE, related_name='upcoming')
    is_next_sunday = models.BooleanField(default=True)
    special_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Upcoming Sermons"
        ordering = ['sermon__date_preached']

    def __str__(self):
        return f"Upcoming: {self.sermon.title}"


class Ministry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='ministries/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ministry_detail', args=[self.slug])
