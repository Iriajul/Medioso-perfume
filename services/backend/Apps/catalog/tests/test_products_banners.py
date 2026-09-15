from datetime import time, timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.catalog.models import Banner, Category, Product
from Apps.common.testing import png

UPLOAD = {"secure_url": "https://res.cloudinary.com/x/new.png", "public_id": "p/new"}
HOURS = {"weekday_opens": time(10), "weekday_closes": time(21), "sunday_opens": time(11), "sunday_closes": time(19)}


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value=UPLOAD)
class ProductApiTests(APITestCase):
    list_url = reverse("v1:catalog:product-list")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        cls.oriental = Category.objects.create(name="Oriental", type="exotic", image_url="https://x/c.png", image_public_id="c/1")
        cls.paris = Branch.objects.create(name="Paris", address="a", phone="1", **HOURS)
        cls.dubai = Branch.objects.create(name="Dubai", address="b", phone="2", **HOURS)
        for i in range(5):
            p = Product.objects.create(name=f"Oud {i}", category=cls.oriental, price="100.00", stock=10 * i,
                                       images=[{"url": f"https://x/{i}.png", "public_id": f"p/{i}"}])
            p.branches.set([cls.paris, cls.dubai])

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")

    def detail(self, product):
        return reverse("v1:catalog:product-detail", args=[product.pk])

    def test_list_no_n_plus_one(self, upload, destroy):
        # auth + count + page (with category join) + branches prefetch + stock sum + revenue sum
        with self.assertNumQueries(6):
            response = self.client.get(self.list_url)

        data = response.json()
        self.assertEqual((data["count"], len(data["results"]), data["in_stock"]), (5, 4, 100))
        first = data["results"][0]
        self.assertEqual(first["category_name"], "Oriental")
        self.assertEqual(first["sku"], f"MAD-{first['id']:03d}")
        self.assertEqual(first["image_urls"][1:], [None, None])
        self.assertEqual(sorted(first["branches"]), sorted([self.paris.pk, self.dubai.pk]))

    def test_create_with_images_and_branches(self, upload, destroy):
        payload = {"name": "Velvet Oud", "category": self.oriental.pk, "price": "185.00", "stock": 12, "is_featured": True,
                   "branches": [self.paris.pk], "image_1": png(), "image_3": png()}
        response = self.client.post(self.list_url, payload, format="multipart")

        self.assertEqual(response.status_code, 201, response.json())
        product = Product.objects.get(pk=response.json()["id"])
        self.assertEqual([bool(i) for i in product.images], [True, False, True])
        self.assertEqual(list(product.branches.all()), [self.paris])
        self.assertTrue(product.is_featured)

    def test_create_requires_an_image(self, upload, destroy):
        response = self.client.post(self.list_url, {"name": "X", "category": self.oriental.pk, "price": "1"}, format="multipart")
        self.assertIn("image_1", response.json())

    def test_put_replaces_slot_and_clears_branches(self, upload, destroy):
        product = Product.objects.get(name="Oud 1")
        payload = {"name": "Oud One", "category": self.oriental.pk, "price": "120.00", "stock": 3, "image_1": png()}
        response = self.client.put(self.detail(product), payload, format="multipart")

        self.assertEqual(response.status_code, 200, response.json())
        product.refresh_from_db()
        self.assertEqual(product.images[0]["public_id"], "p/new")
        self.assertEqual(product.branches.count(), 0)
        self.assertFalse(product.is_featured)
        destroy.assert_called_once_with("p/1", invalidate=True)

    def test_delete_cleans_images(self, upload, destroy):
        product = Product.objects.get(name="Oud 2")
        self.assertEqual(self.client.delete(self.detail(product)).status_code, 204)
        destroy.assert_called_once_with("p/2", invalidate=True)

    def test_category_counts_and_protection(self, upload, destroy):
        response = self.client.get(reverse("v1:catalog:category-list"))
        self.assertEqual(response.json()["results"][0]["products_count"], 5)

        response = self.client.delete(reverse("v1:catalog:category-detail", args=[self.oriental.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Category.objects.filter(pk=self.oriental.pk).exists())

    def test_options_endpoints(self, upload, destroy):
        with self.assertNumQueries(2):
            categories = self.client.get(reverse("v1:catalog:category-options")).json()
        self.assertEqual(categories, [{"id": self.oriental.pk, "name": "Oriental"}])
        branches = self.client.get(reverse("v1:branches:branch-options")).json()
        self.assertEqual({b["name"] for b in branches}, {"Paris", "Dubai"})


@patch("Apps.common.media.cloudinary.uploader.destroy")
@patch("Apps.common.media.cloudinary.uploader.upload", return_value=UPLOAD)
class BannerApiTests(APITestCase):
    url = reverse("v1:catalog:banner-list")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        today = timezone.localdate()
        for title, start, end, active in [("Live", -3, 12, True), ("Soon", 5, 20, True), ("Past", -30, -1, True), ("Off", -3, 12, False)]:
            Banner.objects.create(title=title, image_url="https://x/b.png", image_public_id=f"b/{title}",
                                  starts_on=today + timedelta(days=start), ends_on=today + timedelta(days=end), is_active=active)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")

    def test_list_statuses(self, upload, destroy):
        with self.assertNumQueries(2):
            data = self.client.get(self.url).json()
        self.assertEqual({b["title"]: b["status"] for b in data}, {"Live": "active", "Soon": "scheduled", "Past": "ended", "Off": "hidden"})

    def test_create_and_date_validation(self, upload, destroy):
        today = timezone.localdate()
        bad = {"title": "X", "image": png(), "starts_on": today, "ends_on": today - timedelta(days=1)}
        self.assertIn("ends_on", self.client.post(self.url, bad, format="multipart").json())

        good = {"title": "Summer", "image": png(), "starts_on": today, "ends_on": today + timedelta(days=12), "is_active": True}
        response = self.client.post(self.url, good, format="multipart")
        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(response.json()["status"], "active")
