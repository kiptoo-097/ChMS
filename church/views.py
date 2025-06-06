# church/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Event, Sermon
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add upcoming events (limit to 3)
        context["upcoming_events"] = Event.objects.filter(
            date__gte=timezone.now()
        ).order_by("date")[:3]

        # Add recent sermons (limit to 3)
        context["recent_sermons"] = Sermon.objects.all().order_by("-date")[:3]

        return context


def about_view(request):
    return render(request, "about.html")


def ministries_view(request):
    return render(request, "ministries.html")


def events_view(request):
    events = Event.objects.all()
    return render(request, "events.html", {"events": events})


def contact_view(request):
    return render(request, "contact.html")


@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")
from django.conf import settings


def get_start_datetime(self):
    dt = datetime.combine(self.date, self.time)
    if settings.USE_TZ and timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def get_end_datetime(self):
    if self.end_time:
        dt = datetime.combine(self.date, self.end_time)
        if settings.USE_TZ and timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt
    return None
