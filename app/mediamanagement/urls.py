from django.urls import path
from .views import PublicFileUploadAPIView, PrivateFileUploadAPIView


urlpatterns = [
    path(
        "upload-media/public/",
        PublicFileUploadAPIView.as_view(),
        name="upload-media",
    ),
    path(
        "upload-media/private/",
        PrivateFileUploadAPIView.as_view(),
        name="upload-media",
    ),
]
