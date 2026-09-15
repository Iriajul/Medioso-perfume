from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.catalog.models import Category
from Apps.common.testing import png


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value={"secure_url": "https://res.cloudinary.com/x/new.png", "public_id": "cat/new"})
class CategoryApiTests(APITestCase):
    list_url = reverse("v1:catalog:category-list")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        for i, name in enumerate(["Floral", "Woody", "Oriental", "Fresh", "Musk", "Citrus"]):
            Category.objects.create(name=name, type="classic", image_url=f"https://res.cloudinary.com/x/{i}.png", image_public_id=f"cat/{i}")

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")

    def detail_url(self, pk):
        return reverse("v1:catalog:category-detail", args=[pk])

    def test_list_is_paginated_without_extra_queries(self, upload, destroy):
        # auth user + count + page
        with self.assertNumQueries(3):
            response = self.client.get(self.list_url)

        data = response.json()
        self.assertEqual(data["count"], 6)
        self.assertEqual([c["name"] for c in data["results"]], ["Citrus", "Floral", "Fresh", "Musk", "Oriental"])
        self.assertEqual(data["results"][0]["products_count"], 0)

    def test_create_uploads_image(self, upload, destroy):
        response = self.client.post(self.list_url, {"name": "Amber", "type": "premium", "description": "Warm", "image": png()})

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(response.json()["image_url"], "https://res.cloudinary.com/x/new.png")
        upload.assert_called_once()

    def test_create_requires_image_and_valid_type(self, upload, destroy):
        response = self.client.post(self.list_url, {"name": "Amber", "type": "nope"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {"type"})
        response = self.client.post(self.list_url, {"name": "Amber", "type": "niche"})
        self.assertIn("image", response.json())

    def test_rejects_non_image_file(self, upload, destroy):
        bad = SimpleUploadedFile("x.png", b"not an image", content_type="image/png")
        response = self.client.post(self.list_url, {"name": "Amber", "type": "niche", "image": bad})

        self.assertEqual(response.status_code, 400)
        upload.assert_not_called()

    def test_update_replaces_image_and_deletes_old(self, upload, destroy):
        category = Category.objects.get(name="Floral")
        response = self.client.patch(self.detail_url(category.pk), {"name": "Floral Bloom", "image": png()}, format="multipart")

        self.assertEqual(response.status_code, 200)
        category.refresh_from_db()
        self.assertEqual((category.name, category.image_public_id), ("Floral Bloom", "cat/new"))
        destroy.assert_called_once_with("cat/0", invalidate=True)

    def test_update_without_image_keeps_it(self, upload, destroy):
        category = Category.objects.get(name="Woody")
        response = self.client.patch(self.detail_url(category.pk), {"description": "Earthy"}, format="multipart")

        self.assertEqual(response.status_code, 200)

        upload.assert_not_called()
        destroy.assert_not_called()

    def test_delete_removes_image(self, upload, destroy):
        category = Category.objects.get(name="Musk")
        self.assertEqual(self.client.delete(self.detail_url(category.pk)).status_code, 204)
        destroy.assert_called_once_with("cat/4", invalidate=True)

    def test_requires_admin(self, upload, destroy):
        customer = User.objects.create_user(email="c@madperfume.com", password="x", full_name="C")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(customer)}")
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
