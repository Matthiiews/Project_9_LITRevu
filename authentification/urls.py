from django.urls import path

from .views import (
    signup_page_view, login_page_view, logout_page_view, abo_page_view)

app_name = "authentification"

urlpatterns = [
    path("", login_page_view, name="login"),
    path("logout/", logout_page_view, name="logout"),
    path("signup/", signup_page_view, name="register"),
    path("abo/<str:user>/", abo_page_view, name="abo_page"),
]
