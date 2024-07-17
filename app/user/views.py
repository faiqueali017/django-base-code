"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from user.serializers import (
    UserSerializer,
    GuestUserSerializer,
    AuthTokenSerializer,
    ChangePasswordSerializer,
    OTPRequestSerializer,
    ResetPasswordSerializer,
)


class CreateUserAPIView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateGuestUserAPIView(generics.CreateAPIView):
    """Create a new guest user in the system"""

    serializer_class = GuestUserSerializer


class CreateTokenAPIView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class DeleteTokenAPIView(generics.DestroyAPIView):
    """Delete the token."""

    serializer_class = AuthTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):
        return self.request.user.auth_token


class ManageUserAPIView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_class = [authentication.TokenAuthentication]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class ChangePasswordAPIView(generics.UpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_class = [authentication.TokenAuthentication]
    http_method_names = ["patch"]

    def get_object(self):
        """Retrieve the authenticated user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"success": "Password changed successfully."})


class OTPRequestAPIView(generics.CreateAPIView):
    serializer_class = OTPRequestSerializer


class ResetPasswordAPIView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
