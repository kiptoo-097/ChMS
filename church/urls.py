from django.urls import path
from .views import HomeView, about_view, ministries_view, events_view, contact_view

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", about_view, name="about"),
    path("ministries/", ministries_view, name="ministries"),
    path("events/", events_view, name="events"),
    path("contact/", contact_view, name="contact"),
]


