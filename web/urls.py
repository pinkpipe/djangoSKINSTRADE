from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("home/", views.home, name="home"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("tradelink/", views.save_tradelink, name="tradelink"),
    path("email/", views.save_email, name="email"),
    path("telegram/", views.save_telegram, name="telegram"),
]
