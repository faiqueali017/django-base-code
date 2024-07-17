from django.db import models
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import (
    PermissionsMixin,
    AbstractBaseUser,
    BaseUserManager,
)

from django.utils.translation import gettext_lazy as _


class BaseTimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super(BaseTimestampModel, self).delete(
            using=using,
            keep_parents=keep_parents,
        )

    def restore(self):
        self.deleted_at = None
        self.save()


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)

        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.user_type = User.UserType.ADMIN
        user.is_superuser = True
        user.is_staff = True

        user.save()
        return user


class File(BaseTimestampModel):

    class FileType(models.TextChoices):
        IMAGE = 0, _("Image")
        AUDIO = 1, _("Audio")
        VIDEO = 2, _("Video")

    file_id = models.AutoField(primary_key=True)
    source_url = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices)


class User(AbstractBaseUser, PermissionsMixin, BaseTimestampModel):

    class UserType(models.TextChoices):
        ADMIN = 0, _("Admin")
        GUEST = 1, _("Guest")
        USER = 2, _("User")
        TEST = 3, _("Test")

    user_id = models.AutoField(primary_key=True)

    # Base Attributes
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    image_id = models.OneToOneField(
        File,
        related_name="user_image",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Enumerated Category
    user_type = models.CharField(
        max_length=10,
        default=UserType.GUEST,
        choices=UserType.choices,
    )

    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Additional Configuration
    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ["user_id"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OTP(BaseTimestampModel):
    otp_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.otp_id:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"OTP({self.code}) for {self.user.email}"
