from datetime import time, timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.common.testing import png

HOURS = {"weekday_opens": "10:00", "weekday_closes": "21:00", "sunday_opens": "11:00", "sunday_closes": "19:00"}


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value={"secure_url": "https://res.cloudinary.com/x/b.png", "public_id": "br/new"})
class BranchApiTests(APITestCase):
    list_url = reverse("v1:branches:branch-list")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        hours = {k: time.fromisoformat(v) for k, v in HOURS.items()}
        for name in ["Paris Flagship", "London Bond St.", "NYC 5th Ave", "Dubai Mall", "Tokyo Ginza", "Milan Montenapoleone"]:
            Branch.objects.create(name=name, address=f"{name} address", phone="+1 555", **hours)
        # One branch from a previous quarter.
        Branch.objects.filter(name="Tokyo Ginza").update(created_at=timezone.now() - timedelta(days=200))

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")

    def test_list_paginated_with_quarter_count(self, upload, destroy):
        # auth user + count + page + this-quarter count
        with self.assertNumQueries(4):
            response = self.client.get(self.list_url)

        data = response.json()
        self.assertEqual(data["count"], 6)
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["added_this_quarter"], 5)

    def test_create_without_image(self, upload, destroy):
        payload = {"name": "Riyadh", "address": "King Fahd Rd", "phone": "+966 11", "latitude": "24.713600", "longitude": "46.675300", **HOURS}
        response = self.client.post(self.list_url, payload, format="multipart")

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(response.json()["image_url"], "")
        upload.assert_not_called()

    def test_closing_must_follow_opening(self, upload, destroy):
        payload = {"name": "Riyadh", "address": "x", "phone": "1", **HOURS, "sunday_closes": "10:00"}
        response = self.client.post(self.list_url, payload, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertIn("sunday_closes", response.json())

    def test_update_image_replaces_old(self, upload, destroy):
        branch = Branch.objects.get(name="Dubai Mall")
        Branch.objects.filter(pk=branch.pk).update(image_public_id="br/old")
        response = self.client.patch(reverse("v1:branches:branch-detail", args=[branch.pk]), {"image": png()}, format="multipart")

        self.assertEqual(response.status_code, 200)
        destroy.assert_called_once_with("br/old", invalidate=True)

    def test_delete(self, upload, destroy):
        branch = Branch.objects.get(name="NYC 5th Ave")
        self.assertEqual(self.client.delete(reverse("v1:branches:branch-detail", args=[branch.pk])).status_code, 204)
        destroy.assert_not_called()  # no image to clean up

    def test_requires_admin(self, upload, destroy):
        self.client.credentials()
        self.assertEqual(self.client.get(self.list_url).status_code, 401)
