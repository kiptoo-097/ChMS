from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from .models import Event, Sermon, EventRSVP,Sermon, SermonSeries, UpcomingSermon, Ministry
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class HomeView(TemplateView):
    template_name = "home.html"

    def post(self, request, *args, **kwargs):
        # Here you could process and store the message if desired
        return self.get(request, message_sent=True)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["message_sent"] = kwargs.get("message_sent", False)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Latest trending events (carousel)
        context["trending_events"] = Event.objects.filter(
            is_trending=True, date__gte=timezone.now()
        ).order_by("-date", "-time")[:3]

        # Latest upcoming events (non-trending)
        context["upcoming_events"] = (
            Event.objects.filter(date__gte=timezone.now())
            .exclude(is_trending=True)
            .order_by("date", "time")[:6]
        )

        # Recent featured sermons
        context["recent_sermons"] = Sermon.objects.filter(
            is_featured=True
        ).order_by("-date_preached")[:3]

        # Display a few ministries
        context["ministries"] = Ministry.objects.all()[:3]

        return context

class EventDetailView(DetailView):
    model = Event
    template_name = "event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            try:
                context["user_rsvp"] = EventRSVP.objects.get(event=self.object, user=self.request.user)
            except EventRSVP.DoesNotExist:
                context["user_rsvp"] = None
        else:
            context["user_rsvp"] = None

        return context


@login_required
def event_rsvp(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Only allow RSVP if event hasn't ended
    if event.get_status == "ended":
        messages.error(request, "This event has ended. RSVPs are closed.")
        return redirect(event.get_absolute_url())

    # Get or create the RSVP record for this user and event
    rsvp, created = EventRSVP.objects.get_or_create(event=event, user=request.user)

    if request.method == "POST":
        try:
            attending = request.POST.get("attending") == "on"
            guests = int(request.POST.get("guests", 0))
            notes = request.POST.get("notes", "")

            rsvp.attending = attending
            rsvp.guests = guests
            rsvp.notes = notes
            rsvp.save()

            if attending:
                messages.success(request, "RSVP submitted successfully.")
            else:
                messages.info(request, "You have opted not to attend.")

        except ValueError:
            messages.error(request, "Invalid input. Please check your form.")

        return redirect(event.get_absolute_url())

    return redirect(event.get_absolute_url())




def events_view(request):
    now = timezone.now()
    filter_type = request.GET.get("filter", "all")

    # Get trending events (unchanged)
    trending_events = Event.objects.filter(
        is_trending=True, date__gte=now.date()
    ).order_by("date")[:3]

    # Main events query
    events = Event.objects.all().order_by(
        "-created_at"
    )  # Newest first (reverse chronological)

    # Apply filters
    if filter_type == "upcoming":
        events = events.filter(date__gte=now.date()).exclude(
            pk__in=[e.pk for e in trending_events]
        )
    elif filter_type == "happening":
        events = events.filter(
            date=now.date(), time__lte=now.time(), end_time__gte=now.time()
        )
    elif filter_type == "ended":
        events = events.filter(
            Q(date__lt=now.date())
            | Q(date=now.date(), end_time__lt=now.time())
            | Q(date=now.date(), end_time__isnull=True, time__lt=now.time())
        )

    # Pagination (6 events per page)
    paginator = Paginator(events, 6)
    page_number = request.GET.get("page")
    events_page = paginator.get_page(page_number)

    return render(
        request,
        "events.html",
        {
            "trending_events": trending_events,
            "events": events_page,
            "filter": filter_type,
        },
    )


def about_view(request):
    return render(request, "about.html")



from django.core.paginator import Paginator

def ministries_view(request):
    all_ministries = Ministry.objects.all().order_by('name')
    paginator = Paginator(all_ministries, 6)  # Show 6 per page
    page_number = request.GET.get('page')
    ministries = paginator.get_page(page_number)

    return render(request, "ministries.html", {"ministries": ministries})



def ministry_detail_view(request, slug):
    ministry = get_object_or_404(Ministry, slug=slug)
    return render(request, 'ministry_detail.html', {'ministry': ministry})



def contact_view(request):
    message_sent = False

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # In production, send email or save message here
        message_sent = True

    return render(request, "contact.html", {"message_sent": message_sent})


@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")




def sermon_list(request):
    sermon_list = Sermon.objects.filter(date_preached__lte=timezone.now().date()).order_by('-date_preached')
    
    # Pagination
    paginator = Paginator(sermon_list, 10)  # Show 10 sermons per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get upcoming sermon
    upcoming_sermon = UpcomingSermon.objects.filter(
        sermon__date_preached__gte=timezone.now().date()
    ).order_by('sermon__date_preached').first()
    
    context = {
        'page_obj': page_obj,
        'upcoming_sermon': upcoming_sermon,
    }
    return render(request, 'sermons/sermon_list.html', context)

def sermon_detail(request, pk):
    sermon = get_object_or_404(Sermon, pk=pk)
    related_sermons = Sermon.objects.filter(
        series=sermon.series
    ).exclude(pk=pk).order_by('-date_preached')[:3]
    
    context = {
        'sermon': sermon,
        'related_sermons': related_sermons,
    }
    return render(request, 'sermons/sermon_detail.html', context)

def sermon_series_list(request):
    series_list = SermonSeries.objects.all().order_by('-start_date')
    context = {
        'series_list': series_list,
    }
    return render(request, 'sermons/series_list.html', context)

def sermon_series_detail(request, pk):
    series = get_object_or_404(SermonSeries, pk=pk)
    sermons = series.sermons.all().order_by('-date_preached')
    
    context = {
        'series': series,
        'sermons': sermons,
    }
    return render(request, 'sermons/series_detail.html', context)


@login_required
def join_ministry(request, pk):
    ministry = get_object_or_404(Ministry, pk=pk)

    if request.user in ministry.members.all():
        messages.info(request, "You have already joined this ministry.")
    else:
        ministry.members.add(request.user)
        messages.success(request, f"You have successfully joined {ministry.name}!")

    return redirect(ministry.get_absolute_url())
