"""
URL mappings for the user API.
"""

from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path("user/signup/", views.CreateUserAPIView().as_view(), name="signup"),
    path(
        "user/signin-guest/",
        views.CreateGuestUserAPIView().as_view(),
        name="signin-guest",
    ),
    path("user/signin/", views.CreateTokenAPIView().as_view(), name="signin"),
    path("user/logout/", views.DeleteTokenAPIView().as_view(), name="logout"),
    path("user/profile/", views.ManageUserAPIView().as_view(), name="profile"),
    path(
        "user/change-password/",
        views.ChangePasswordAPIView().as_view(),
        name="change-password",
    ),
    path(
        "user/reset-password-otp/",
        views.OTPRequestAPIView().as_view(),
        name="send-otp",
    ),
    path(
        "user/reset-password/",
        views.ResetPasswordAPIView().as_view(),
        name="reset-password",
    ),
]
