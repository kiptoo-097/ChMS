# church/admin.py
from django.contrib import admin
from .models import Event, Sermon


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "time",
        "end_time",
        "location",
        "category",
        "created_by",
    )
    list_filter = ("category", "date", "created_by")
    search_fields = ("title", "description", "location")
    date_hierarchy = "date"
    ordering = ("-date", "-time")
    fieldsets = (
        ("Basic Information", {"fields": ("title", "description", "category")}),
        ("Date and Time", {"fields": ("date", "time", "end_time")}),
        ("Location", {"fields": ("location",)}),
        ("Media", {"fields": ("image",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_by",), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by during the first save
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SermonAdmin(admin.ModelAdmin):
    list_display = ("title", "preacher", "date", "topic", "bible_verse")
    list_filter = ("date", "preacher")
    search_fields = ("title", "preacher", "topic", "bible_verse")
    date_hierarchy = "date"
    ordering = ("-date",)
    fieldsets = (
        (
            "Sermon Details",
            {"fields": ("title", "preacher", "date", "topic", "bible_verse")},
        ),
        (
            "Media Files",
            {"fields": ("audio_file", "video_url", "notes"), "classes": ("collapse",)},
        ),
    )


admin.site.register(Event, EventAdmin)
admin.site.register(Sermon, SermonAdmin)
