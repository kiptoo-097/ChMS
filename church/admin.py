from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventRSVP, Sermon
from django.urls import reverse
from django.utils import timezone


class EventRSVPInline(admin.TabularInline):
    model = EventRSVP
    extra = 0
    readonly_fields = ("created_at", "updated_at", "rsvp_status")
    fields = ("user", "rsvp_status", "guests", "notes", "created_at", "updated_at")
    ordering = ("-created_at",)

    def rsvp_status(self, obj):
        if obj.attending:
            return format_html('<span style="color: green;">✓ Attending</span>')
        return format_html('<span style="color: red;">✗ Not Attending</span>')

    rsvp_status.short_description = "Status"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date_time_display",
        "category",
        "trending_status",
        "registration_status",
        "created_by",
        "status_badge",
    )
    list_filter = (
        "category",
        "is_trending",
        "date",
        "created_by",
        ("created_at", admin.DateFieldListFilter),
    )
    search_fields = ("title", "description", "location")
    date_hierarchy = "date"
    ordering = ("-date", "-time")
    inlines = [EventRSVPInline]
    readonly_fields = (
        "status_badge",
        "available_seats_display",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Event Information",
            {"fields": ("title", "description", "category", "is_trending")},
        ),
        ("Date & Time", {"fields": ("date", "time", "end_time")}),
        (
            "Location & Capacity",
            {"fields": ("location", "max_attendees", "available_seats_display")},
        ),
        ("Media", {"fields": ("image",), "classes": ("collapse",)}),
        (
            "Status & Metadata",
            {
                "fields": ("status_badge", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def date_time_display(self, obj):
        time_str = obj.time.strftime("%I:%M %p")
        if obj.end_time:
            time_str += f" - {obj.end_time.strftime('%I:%M %p')}"
        return format_html(
            '<div>{}</div><small class="text-muted">{}</small>',
            obj.date.strftime("%b %d, %Y"),
            time_str,
        )

    date_time_display.short_description = "Date & Time"
    date_time_display.admin_order_field = "date"

    def trending_status(self, obj):
        if obj.is_trending:
            return format_html('<span style="color: #ffc107;">★ Trending</span>')
        return "-"

    trending_status.short_description = "Trending"

    def registration_status(self, obj):
        if obj.max_attendees:
            return f"{obj.available_seats()}/{obj.max_attendees}"
        return "Open"

    registration_status.short_description = "Seats"

    def status_badge(self, obj):
        try:
            status = obj.get_status
        except Exception:
            status = "unspecified"

        color_map = {
            "happening": ("red", "Happening Now!"),
            "ended": ("gray", "Ended"),
            "upcoming": ("green", "Upcoming"),
            "unspecified": ("orange", "Date/Time Missing"),
        }

        color, label = color_map.get(status, ("black", "Unknown"))

        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 6px; border-radius: 4px;">{}</span>',
            color,
            label
        )

    status_badge.short_description = "Status"


    def available_seats_display(self, obj):
        seats = obj.available_seats()
        if seats == "Unlimited":
            return seats
        percentage = (int(seats) / obj.max_attendees) * 100
        if percentage < 20:
            color = "#dc3545"
        elif percentage < 50:
            color = "#fd7e14"
        else:
            color = "#28a745"
        return format_html(
            '<div style="width: 100%; background-color: #e9ecef; border-radius: 4px;">'
            '<div style="width: {}%; background-color: {}; height: 24px; border-radius: 4px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">'
            "{} left</div></div>",
            percentage,
            color,
            seats,
        )

    available_seats_display.short_description = "Availability"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("rsvps")


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = (
        "event_title",
        "user_display",
        "attending_status",
        "total_attendees",
        "created_at_display",
    )
    list_filter = (
        "attending",
        ("event__date", admin.DateFieldListFilter),
        "created_at",
    )
    search_fields = (
        "event__title",
        "user__first_name",
        "user__last_name",
        "user__username",
    )
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def event_title(self, obj):
        url = reverse("admin:church_event_change", args=[obj.event.id])
        return format_html('<a href="{}">{}</a>', url, obj.event.title)

    event_title.short_description = "Event"
    event_title.admin_order_field = "event__title"

    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_display.short_description = "User"
    user_display.admin_order_field = "user__username"

    def attending_status(self, obj):
        if obj.attending:
            return format_html(
                '<span style="color: green;">✓ Attending ({})</span>',
                obj.total_attendees(),
            )
        return format_html('<span style="color: red;">✗ Not Attending</span>')

    attending_status.short_description = "Status"

    def created_at_display(self, obj):
        from django.utils.timezone import localtime
        local_dt = localtime(obj.created_at)
        return local_dt.strftime("%b %d, %Y %I:%M %p")

    created_at_display.short_description = "RSVP Date"
    created_at_display.admin_order_field = "created_at"


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "preacher",
        "date",
        "sermon_type",
        "is_featured",
        "media_links",
    )
    list_filter = ("sermon_type", "is_featured", "date", "preacher")
    search_fields = ("title", "preacher", "topic", "bible_verse")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at", "media_preview")
    fieldsets = (
        (
            "Sermon Details",
            {"fields": ("title", "preacher", "date", "sermon_type", "is_featured")},
        ),
        ("Content", {"fields": ("topic", "bible_verse", "scripture_text", "summary")}),
        ("Media", {"fields": ("audio_file", "video_url", "slides", "media_preview")}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def media_links(self, obj):
        links = []
        if obj.audio_file:
            links.append(
                format_html(
                    '<a href="{}" target="_blank" title="Audio"><i class="bi bi-file-earmark-music"></i></a>',
                    obj.audio_file.url,
                )
            )
        if obj.video_url:
            links.append(
                format_html(
                    '<a href="{}" target="_blank" title="Video"><i class="bi bi-film"></i></a>',
                    obj.video_url,
                )
            )
        if obj.slides:
            links.append(
                format_html(
                    '<a href="{}" target="_blank" title="Slides"><i class="bi bi-file-earmark-ppt"></i></a>',
                    obj.slides.url,
                )
            )
        return format_html(" ".join(links)) if links else "-"

    media_links.short_description = "Media"

    def media_preview(self, obj):
        if obj.video_url:
            return format_html(
                '<div style="margin-top: 10px;">'
                "<h4>Video Preview</h4>"
                '<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">'
                '<iframe src="{}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" '
                "allowfullscreen></iframe></div></div>",
                obj.video_url.replace("watch?v=", "embed/"),
            )
        return "-"

    media_preview.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
