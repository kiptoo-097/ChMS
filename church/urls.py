# church/urls.py
from django.urls import path
from .views import (
    HomeView,
    about_view,
    ministries_view,
    events_view,
    contact_view,
    profile_view,
    dashboard_view,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", about_view, name="about"),
    path("ministries/", ministries_view, name="ministries"),
    path("events/", events_view, name="events"),
    path("contact/", contact_view, name="contact"),
    path("profile/", profile_view, name="profile"),
    path("dashboard/", dashboard_view, name="dashboard"),
]
