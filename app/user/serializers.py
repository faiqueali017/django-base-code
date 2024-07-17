"""
Serializers for the user API View.
"""

import random
import string
from datetime import datetime
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from core.models import User, File, OTP

from common.mail import send_otp_email


class FileSerializer(serializers.ModelSerializer):
    """Serializer for the File model."""

    class Meta:
        model = File
        fields = [
            "file_id",
            "source_url",
            "file_type",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = [
            "user_id",
            "email",
            "password",
            "first_name",
            "last_name",
            "image_id",
            "user_type",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
            },  # Ensures password is write-only
            "image_id": {"required": False},  # Allows image_id to be optional
        }

    def validate(self, data):
        """Validate the user data."""
        if self.instance is None and "user_type" in data:
            # If creating a new user and user_type is provided, validate it
            self.validate_user_type(data["user_type"])
        return data

    def validate_user_type(self, value):
        """Validate user_type."""
        if value == User.UserType.ADMIN:
            raise serializers.ValidationError(
                "User type 'Admin' is not allowed.",
            )
        return value

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user (not password)."""

        validated_data.pop("password", None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        image_obj = FileSerializer(instance.image_id).data
        return {
            "user_id": instance.user_id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "user_type": instance.user_type,
            "image": (image_obj if instance.image_id else None),
        }


class GuestUserSerializer(serializers.Serializer):
    def create(self, validated_data):
        """Create and return a guest user."""
        random_number = "".join(
            random.choices(
                string.digits,
                k=random.randint(3, 4),
            )
        )
        email = f"guest{random_number}@gmail.com"
        password = "guestpassword123"
        first_name = f"guest{random_number} FN"
        last_name = f"guest{random_number} LN"
        user_type = User.UserType.GUEST
        return get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
        )

    def to_representation(self, instance):
        """Serialize instance to return token."""
        token, _ = Token.objects.get_or_create(user=instance)
        return {"token": f"{token}"}


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("requests"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""

    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        """Validate the password."""

        old = attrs.get("old_password")
        new = attrs.get("new_password")

        request = self.context.get("request")
        email = request.user.email

        user = authenticate(
            request=request,
            username=email,
            password=old,
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")

        if old == new:
            msg = _("New password cannot be the same as old password")
            raise serializers.ValidationError(msg, code="authorization")

        return attrs

    def update(self, instance, validated_data):
        """Update the password."""

        password = validated_data.get("new_password", None)
        instance.set_password(password)
        instance.save()

        return validated_data


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email does not exist.",
            )
        return value

    def create(self, validated_data):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        otp_code = "{:06d}".format(random.randint(0, 999999))
        otp = OTP(code=otp_code, user=user)
        otp.save()

        message = "Failed to sent OTP"
        if send_otp_email(to_email=user.email, code=otp_code):
            message = "OTP sent successfull"

        return {"message": message, "email": email}

    def to_representation(self, instance):
        return {"message": instance["message"]}


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=6, max_length=128)

    def validate(self, data):
        email = data.get("email")
        code = data.get("code")

        # Check if user exists for the provided email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this email does not exist.",
            )

        # Check if OTP code exists for the user
        try:
            otp = OTP.objects.filter(user=user).order_by("-created_at").first()
            print(otp)

        except OTP.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid OTP code for this user.",
            )

        if otp.code != code:
            raise serializers.ValidationError("Invalid OTP code.")

        if otp.used_at is not None:
            raise serializers.ValidationError("OTP has already been used.")

        if otp.is_expired():
            raise serializers.ValidationError("OTP code has expired.")

        return data

    def create(self, validated_data):
        email = validated_data.get("email")
        new_password = validated_data.get("new_password")

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        otp = OTP.objects.filter(user=user).order_by("-created_at").first()
        otp.used_at = datetime.now()
        otp.save()

        return validated_data

    def to_representation(self, instance):
        return {"message": "Password reset successfully."}
