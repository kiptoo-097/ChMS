# church/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Event, Sermon
from django.utils import timezone


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
    return render(request, "events.html")


def contact_view(request):
    return render(request, "contact.html")
