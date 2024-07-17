from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


VERSION = "v1"

SIGNUP_URL = reverse("user:signup", args=[VERSION])
SIGNIN_URL = reverse("user:signin", args=[VERSION])
LOGOUT_URL = reverse("user:logout", args=[VERSION])
PROFILE_URL = reverse("user:profile", args=[VERSION])
CHANGE_PASSWORD_URL = reverse("user:change-password", args=[VERSION])

user_model = get_user_model()


def create_user(**params):
    """Create and return a new user."""
    return user_model.objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = user_model.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_admin_fails(self):
        """Test creating admin user fails."""

        payload = {
            "user_type": user_model.UserType.ADMIN,
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_model.objects.filter(email=payload["email"]).exists())

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        create_user(**payload)
        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that an error is returned if the password is less than
        8 chars."""

        payload = {
            "email": "test@example.com",
            "password": "passwrd",
            "first_name": "Test",
            "last_name": "User",
        }
        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_model.objects.filter(email=payload["email"]).exists())

    def test_create_token_for_user(self):
        """Test generating tokens for valid credentials."""

        user_details = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = self.client.post(SIGNIN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""

        create_user(email="test@example.com", password="goodpass")

        payload = {"email": "test@example.com", "password": "badpass"}
        res = self.client.post(SIGNIN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test returns error if blank password posted."""

        payload = {"email": "test@example.com", "password": ""}
        res = self.client.post(SIGNIN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_token_unauthorized(self):
        """Test authentication is required for logout."""

        res = self.client.delete(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_password_unauthorized(self):
        """Test authentication is required for changing password."""

        res = self.client.patch(CHANGE_PASSWORD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test the private features of the user API."""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["first_name"], self.user.first_name)
        self.assertEqual(res.data["last_name"], self.user.last_name)
        self.assertEqual(res.data["email"], self.user.email)

    def test_post_profile_not_allowed(self):
        """Test POST method is disabled for the profile endpoint."""

        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for an authenticated user."""

        payload = {"first_name": "Updated", "last_name": "Name"}

        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_password_fails(self):
        """Test updating user profile for an authenticated user."""

        payload = {"first_name": "Updated", "password": "newpassword"}

        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertNotEqual(self.user.password, payload["password"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_token_success(self):
        """Test deleting token for an authenticated user."""

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        res = self.client.post(SIGNIN_URL, payload)

        res = self.client.delete(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_update_password_bad_credentials(self):
        """Test changing password with bad credentials."""

        payload = {
            "old_password": "wrongpassword",
            "new_password": "shouldnotchange",
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_same_password(self):
        """Test changing password with bad credentials."""

        payload = {
            "old_password": "testpass123",
            "new_password": "testpass123",
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_success(self):
        """Test changing password with bad credentials."""

        payload = {
            "old_password": "testpass123",
            "new_password": "newpassword",
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload["new_password"]))
