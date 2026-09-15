from datetime import time
from unittest.mock import patch

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.common.testing import png
from Apps.notifications.models import Notification

HOURS = {"weekday_opens": time(10), "weekday_closes": time(21), "sunday_opens": time(11), "sunday_closes": time(19)}


class Base(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(email="admin@madperfume.com", password="Old-pass-123", full_name="Admin")
        cls.paris = Branch.objects.create(name="Paris", address="a", phone="1", **HOURS)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value={"secure_url": "https://x/s.png", "public_id": "s/new"})
class StaffApiTests(Base):
    url = reverse("v1:accounts:staff-list")

    def test_create_invites_by_email(self, upload, destroy):
        payload = {"full_name": "Julian Vasseur", "email": "julian.v@madperfume.com", "branch": self.paris.pk,
                   "job_title": "master_nose", "is_active": True, "photo": png()}
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, payload, format="multipart")

        self.assertEqual(response.status_code, 201, response.json())
        staff = User.objects.get(email="julian.v@madperfume.com")
        self.assertTrue(staff.is_staff and not staff.is_superuser and not staff.has_usable_password())
        self.assertEqual((staff.avatar_url, response.json()["branch_name"]), ("https://x/s.png", "Paris"))
        self.assertEqual(mail.outbox[0].subject, "Welcome to the Mad Perfume team")
        self.assertIn("/reset-password?uid=", mail.outbox[0].body)

    def test_list_excludes_admins_no_n_plus_one(self, upload, destroy):
        for i in range(5):
            User.objects.create_user(email=f"s{i}@madperfume.com", password=None, full_name=f"S {i}", is_staff=True,
                                     branch=self.paris, job_title="senior_advisor", is_active=i != 0)
        # auth + count + page (branch join) + stats
        with self.assertNumQueries(4):
            data = self.client.get(self.url).json()
        self.assertEqual((data["count"], len(data["results"]), data["total_staff"], data["active_staff"]), (5, 4, 5, 4))
        self.assertEqual(data["results"][0]["branch_name"], "Paris")

    def test_branch_and_role_required(self, upload, destroy):
        response = self.client.post(self.url, {"full_name": "X", "email": "x@madperfume.com"}, format="multipart")
        self.assertEqual(set(response.json()), {"branch", "job_title"})

    def test_role_must_be_a_known_choice(self, upload, destroy):
        payload = {"full_name": "X", "email": "x@madperfume.com", "branch": self.paris.pk, "job_title": "Anything I type"}
        self.assertIn("job_title", self.client.post(self.url, payload, format="multipart").json())


class NotificationTests(Base):
    def test_audience_counts(self):
        for email, points in [("a@x.com", 0), ("b@x.com", 3000), ("c@x.com", 8000), ("d@x.com", 20000)]:
            User.objects.create_user(email=email, password=None, full_name=email, lifetime_points=points)
        url = reverse("v1:notifications:notification-list")
        counts = {}
        for audience in ["all", "gold", "platinum", "diamond"]:
            counts[audience] = self.client.post(url, {"title": "Launch", "body": "Midnight Jasmine", "audience": audience}).json()["recipients_count"]
        self.assertEqual(counts, {"all": 4, "gold": 1, "platinum": 1, "diamond": 1})
        self.assertEqual(Notification.objects.filter(created_by=self.admin, status="sent").count(), 4)


class SecurityTests(Base):
    url = reverse("v1:accounts:change-password")

    def test_change_password_revokes_sessions(self):
        RefreshToken.for_user(self.admin)
        response = self.client.post(self.url, {"current_password": "Old-pass-123", "password": "Brand-new-pass-9"})

        self.assertEqual(response.status_code, 204)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("Brand-new-pass-9"))
        self.assertEqual(BlacklistedToken.objects.count(), 1)
        self.assertIsNotNone(self.client.get(reverse("v1:accounts:me")).json()["password_changed_at"])

    def test_rules(self):
        wrong = self.client.post(self.url, {"current_password": "nope", "password": "Brand-new-pass-9"}).json()
        self.assertIn("current_password", wrong)
        weak = self.client.post(self.url, {"current_password": "Old-pass-123", "password": "longpassword"}).json()
        self.assertTrue(any("number" in m for m in weak["password"]))
        no_symbol = self.client.post(self.url, {"current_password": "Old-pass-123", "password": "longpassword9"}).json()
        self.assertTrue(any("special character" in m for m in no_symbol["password"]))
