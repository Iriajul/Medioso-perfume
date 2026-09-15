import re
from unittest.mock import patch

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import DeviceToken, PasswordResetCode, User
from Apps.common.testing import png

PASSWORD = "Velvet-oud-2026"


class AppAuthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(email="julian@example.com", password=PASSWORD, full_name="Julian Thorne", phone="+33142685300")

    def test_register_returns_tokens(self):
        payload = {"full_name": "Christian Dior", "email": "Christian@Example.com", "phone": "+15550000000", "password": PASSWORD}
        response = self.client.post(reverse("v1:accounts:app-register"), payload)

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(set(response.json()), {"access", "refresh"})
        user = User.objects.get(email="christian@example.com")
        self.assertFalse(user.is_staff)
        self.assertEqual(AccessToken(response.json()["access"])["full_name"], "Christian Dior")

    def test_register_rejects_duplicates_and_weak_password(self):
        payload = {"full_name": "X", "email": "JULIAN@example.com", "phone": "+33142685300", "password": "short"}
        errors = self.client.post(reverse("v1:accounts:app-register"), payload).json()
        self.assertEqual(set(errors), {"email", "phone"})
        payload.update(email="new@example.com", phone="+1999")
        self.assertIn("password", self.client.post(reverse("v1:accounts:app-register"), payload).json())

    def test_login_with_email_or_phone(self):
        url = reverse("v1:accounts:app-login")
        for identifier in ["JULIAN@example.com", "+33142685300"]:
            response = self.client.post(url, {"identifier": identifier, "password": PASSWORD})
            self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(self.client.post(url, {"identifier": "+33142685300", "password": "wrong"}).status_code, 400)

    def test_password_reset_code_flow(self):
        self.client.post(reverse("v1:accounts:app-reset-code"), {"email": "julian@example.com"})
        code = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)
        verify = reverse("v1:accounts:app-reset-verify")

        wrong = "000000" if code != "000000" else "111111"
        self.assertEqual(self.client.post(verify, {"email": "julian@example.com", "code": wrong}).status_code, 400)
        response = self.client.post(verify, {"email": "julian@example.com", "code": code})
        self.assertEqual(response.status_code, 200, response.json())

        confirm = self.client.post(reverse("v1:accounts:password-reset-confirm"), {**response.json(), "password": "New-scent-2027"})
        self.assertEqual(confirm.status_code, 204)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.check_password("New-scent-2027"))
        # The code is single use.
        self.assertEqual(self.client.post(verify, {"email": "julian@example.com", "code": code}).status_code, 400)

    def test_reset_code_locks_after_attempts(self):
        self.client.post(reverse("v1:accounts:app-reset-code"), {"email": "julian@example.com"})
        code = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)
        PasswordResetCode.objects.update(attempts=PasswordResetCode.MAX_ATTEMPTS)
        self.assertEqual(self.client.post(reverse("v1:accounts:app-reset-verify"), {"email": "julian@example.com", "code": code}).status_code, 400)

    def test_reset_code_unknown_email_is_silent(self):
        self.assertEqual(self.client.post(reverse("v1:accounts:app-reset-code"), {"email": "nobody@example.com"}).status_code, 204)
        self.assertEqual(mail.outbox, [])


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value={"secure_url": "https://x/a.png", "public_id": "a/1"})
class AppProfileTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(email="julian@example.com", password=PASSWORD, full_name="Julian Thorne", phone="+331")
        User.objects.create_user(email="other@example.com", password=PASSWORD, full_name="Other", phone="+332")

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")

    def test_get_and_update_profile(self, upload, destroy):
        with self.assertNumQueries(1):
            data = self.client.get(reverse("v1:accounts:app-me")).json()
        self.assertEqual((data["tier"], data["language"], data["push_enabled"]), ("silver", "en", True))

        payload = {"full_name": "Julian T.", "shipping_address": "22 Place Vendôme", "language": "ar", "notify_collections": "false", "avatar": png()}
        response = self.client.patch(reverse("v1:accounts:app-me"), payload, format="multipart")
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual((response.json()["avatar_url"], response.json()["language"], response.json()["notify_collections"]), ("https://x/a.png", "ar", False))

    def test_profile_rejects_taken_phone(self, upload, destroy):
        self.assertIn("phone", self.client.patch(reverse("v1:accounts:app-me"), {"phone": "+332"}).json())

    def test_change_password(self, upload, destroy):
        url = reverse("v1:accounts:app-change-password")
        self.assertEqual(self.client.post(url, {"current_password": PASSWORD, "password": "Another-scent-9"}).status_code, 204)

    def test_device_tokens(self, upload, destroy):
        self.client.post(reverse("v1:accounts:app-devices"), {"token": "fcm-abc", "platform": "ios"})
        self.client.post(reverse("v1:accounts:app-devices"), {"token": "fcm-abc", "platform": "ios"})
        self.assertEqual(DeviceToken.objects.filter(user=self.customer).count(), 1)
        self.assertEqual(self.client.delete(reverse("v1:accounts:app-device", args=["fcm-abc"])).status_code, 204)
        self.assertFalse(DeviceToken.objects.exists())
