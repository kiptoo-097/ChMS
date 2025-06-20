

from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return resolve_url("home")  # or your dashboard

    def get_signup_redirect_url(self, request):
        return resolve_url("account_login")  # redirect to login after signup
