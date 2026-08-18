from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="trails/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("hikes/", views.hike_list, name="hike_list"),
    path("hikes/add/", views.hike_add, name="hike_add"),
    path("hikes/<int:pk>/", views.hike_detail, name="hike_detail"),
    path("hikes/<int:pk>/edit/", views.hike_edit, name="hike_edit"),
    path("hikes/<int:pk>/delete/", views.hike_delete, name="hike_delete"),
]
