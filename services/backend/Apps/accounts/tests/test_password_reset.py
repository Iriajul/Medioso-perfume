import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from Apps.accounts.models import User


class PasswordResetTests(TestCase):
    request_url = reverse("v1:accounts:password-reset")
    confirm_url = reverse("v1:accounts:password-reset-confirm")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="old-pass-123", full_name="Admin", is_staff=True)
        User.objects.create_user(email="customer@madperfume.com", password="old-pass-123", full_name="Customer")

    def post(self, url, data):
        return self.client.post(url, data, content_type="application/json")

    def request_link(self):
        self.post(self.request_url, {"email": "ADMIN@madperfume.com"})
        uid, token = re.search(r"uid=([\w-]+)&token=([\w-]+)", mail.outbox[-1].body).groups()
        return uid, token

    def test_admin_receives_reset_link(self):
        with self.assertNumQueries(1):
            response = self.post(self.request_url, {"email": "admin@madperfume.com"})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(mail.outbox[0].to, ["admin@madperfume.com"])
        self.assertIn("/reset-password?uid=", mail.outbox[0].body)
        html, mimetype = mail.outbox[0].alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn('href="http://localhost:3000/reset-password?uid=', html)

    def test_unknown_or_non_staff_email_sends_nothing(self):
        for email in ["nobody@madperfume.com", "customer@madperfume.com"]:
            self.assertEqual(self.post(self.request_url, {"email": email}).status_code, 204)
        self.assertEqual(mail.outbox, [])

    def test_confirm_sets_password_and_revokes_sessions(self):
        RefreshToken.for_user(self.admin)
        uid, token = self.request_link()

        # user lookup, password update, outstanding tokens select, blacklist insert
        with self.assertNumQueries(4):
            response = self.post(self.confirm_url, {"uid": uid, "token": token, "password": "brand-new-pass-456"})

        self.assertEqual(response.status_code, 204)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("brand-new-pass-456"))
        self.assertEqual(BlacklistedToken.objects.count(), 1)
        # The link is single-use: the token is tied to the old password hash.
        self.assertEqual(self.post(self.confirm_url, {"uid": uid, "token": token, "password": "another-pass-789"}).status_code, 400)

    def test_invalid_token_rejected(self):
        uid, _ = self.request_link()
        response = self.post(self.confirm_url, {"uid": uid, "token": "bad-token", "password": "brand-new-pass-456"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("token", response.json())

    def test_weak_password_rejected(self):
        uid, token = self.request_link()
        response = self.post(self.confirm_url, {"uid": uid, "token": token, "password": "123"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())
