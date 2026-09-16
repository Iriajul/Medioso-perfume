from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import DeviceToken, User
from Apps.notifications import push
from Apps.notifications.models import UserNotification

CREDS = '{"project_id": "mad-perfume", "type": "service_account"}'


class FakeResponse:
    def __init__(self, status_code):
        self.status_code, self.text = status_code, ""


class PushTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sophia = User.objects.create_user(email="sophia@example.com", password="x", full_name="Sophia")
        cls.julien = User.objects.create_user(email="julien@example.com", password="x", full_name="Julien", notify_rewards=False)
        cls.quiet = User.objects.create_user(email="quiet@example.com", password="x", full_name="Quiet", push_enabled=False)
        for n, user in enumerate([cls.sophia, cls.julien, cls.quiet]):
            DeviceToken.objects.create(user=user, token=f"tok-{n}", platform="ios")

    def setUp(self):
        push._session = push._project_id = None

    def notify(self, user, category="rewards"):
        return UserNotification.objects.create(user=user, category=category, title="Gold Status Achievement", body="Congratulations")

    def test_no_credentials_means_inbox_only(self):
        with override_settings(FIREBASE_CREDENTIALS=""):
            self.assertEqual(push.send([self.notify(self.sophia)]), 0)

    @override_settings(FIREBASE_CREDENTIALS=CREDS)
    @patch("google.oauth2.service_account.Credentials.from_service_account_info")
    @patch("google.auth.transport.requests.AuthorizedSession")
    def test_respects_preferences_and_drops_dead_tokens(self, session_class, creds):
        session = session_class.return_value
        session.post.return_value = FakeResponse(200)
        notifications = [self.notify(u) for u in (self.sophia, self.julien, self.quiet)]

        # Julien muted reward alerts, Quiet muted push entirely: only Sophia is messaged.
        self.assertEqual(push.send(notifications), 1)
        message = session.post.call_args.kwargs["json"]["message"]
        self.assertEqual((message["token"], message["notification"]["title"]), ("tok-0", "Gold Status Achievement"))
        self.assertEqual(message["data"]["category"], "rewards")

        session.post.return_value = FakeResponse(404)  # token no longer registered
        self.assertEqual(push.send([self.notify(self.sophia)]), 0)
        self.assertFalse(DeviceToken.objects.filter(token="tok-0").exists())

    @override_settings(FIREBASE_CREDENTIALS=CREDS)
    @patch("google.oauth2.service_account.Credentials.from_service_account_info")
    @patch("google.auth.transport.requests.AuthorizedSession")
    def test_order_notification_carries_the_order_id(self, session_class, creds):
        session_class.return_value.post.return_value = FakeResponse(200)
        note = self.notify(self.sophia, category="orders")
        push.send([note])
        self.assertEqual(session_class.return_value.post.call_args.kwargs["json"]["message"]["data"]["order_id"], "")


class BroadcastPushTests(APITestCase):
    @override_settings(FIREBASE_CREDENTIALS="")
    def test_admin_broadcast_still_fills_inboxes(self):
        admin = User.objects.create_superuser(email="admin@madperfume.com", password="x", full_name="Admin")
        User.objects.create_user(email="c@example.com", password="x", full_name="C")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(admin)}")
        response = self.client.post(reverse("v1:notifications:notification-list"),
                                    {"title": "Private Sale", "body": "20% off", "audience": "all"})
        self.assertEqual((response.status_code, response.json()["recipients_count"]), (201, 1))
        self.assertEqual(UserNotification.objects.filter(category="offers").count(), 1)
