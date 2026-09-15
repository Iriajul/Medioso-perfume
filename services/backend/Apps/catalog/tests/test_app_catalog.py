from datetime import time, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.catalog.models import Banner, Category, Product, Review, SavedProduct
from Apps.loyalty.models import LoyaltyTransaction
from Apps.orders.models import Order, OrderItem

HOURS = {"weekday_opens": time(10), "weekday_closes": time(20), "sunday_opens": time(11), "sunday_closes": time(19)}


class AppCatalogTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(email="c@example.com", password="x", full_name="Sophia R.")
        cls.woody = Category.objects.create(name="Woody", type="classic", image_url="https://x/w.png", image_public_id="w")
        cls.floral = Category.objects.create(name="Floral", type="classic", image_url="https://x/f.png", image_public_id="f")
        cls.paris = Branch.objects.create(name="Place Vendôme", address="a", city="Paris", country="France", phone="1", latitude=48.8675, longitude=2.3294, **HOURS)
        cls.london = Branch.objects.create(name="Mayfair", address="b", city="London", country="UK", phone="2", latitude=51.5112, longitude=-0.1426, **HOURS)
        Branch.objects.create(name="No Coords", address="c", city="Dubai", phone="3", **HOURS)
        img = [{"url": "https://x/p.png", "public_id": "p"}]
        cls.oud = Product.objects.create(name="Oud Minimaliste", category=cls.woody, price="240.00", stock=5, notes="Oud Noir, Bergamot", images=img, is_featured=True)
        cls.noir = Product.objects.create(name="Midnight Noir", category=cls.woody, price="185.00", stock=0, images=img)
        cls.bloom = Product.objects.create(name="Golden Bloom", category=cls.floral, price="210.00", stock=3, brand="Aurélia", images=img)
        cls.oud.branches.set([cls.paris])
        other = User.objects.create_user(email="o@example.com", password="x", full_name="James L.")
        Review.objects.create(product=cls.oud, user=other, rating=5, comment="Masterpiece")
        Review.objects.create(product=cls.oud, user=User.objects.create_user(email="p@example.com", password="x", full_name="P"), rating=4)
        order = Order.objects.create(customer=other, total=Decimal("420"), payment_method="card", status="delivered")
        OrderItem.objects.create(order=order, product=cls.noir, product_name="Midnight Noir", sku="x", unit_price="185", quantity=2)
        today = timezone.localdate()
        Banner.objects.create(title="Velvet Oud Edition", image_url="https://x/b.png", image_public_id="b", starts_on=today - timedelta(days=1), ends_on=today + timedelta(days=5))
        Banner.objects.create(title="Past", image_url="https://x/b.png", image_public_id="b2", starts_on=today - timedelta(days=9), ends_on=today - timedelta(days=2))

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")

    def test_public_home_data(self):
        self.assertEqual([c["name"] for c in self.client.get(reverse("v1:catalog:app-categories")).json()], ["Floral", "Woody"])
        self.assertEqual([b["title"] for b in self.client.get(reverse("v1:catalog:app-banners")).json()], ["Velvet Oud Edition"])

    def test_product_list_single_query_page(self):
        self.auth()
        # auth + count + page (rating/reviews/sold/saved as subqueries)
        with self.assertNumQueries(3):
            data = self.client.get(reverse("v1:catalog:app-product-list")).json()
        oud = next(p for p in data["results"] if p["name"] == "Oud Minimaliste")
        self.assertEqual((oud["rating"], oud["reviews_count"], oud["notes"], oud["is_saved"], oud["in_stock"]), (4.5, 2, ["Oud Noir", "Bergamot"], False, True))

    def test_search_filters_and_sorting(self):
        url = reverse("v1:catalog:app-product-list")
        names = lambda params: [p["name"] for p in self.client.get(url, params).json()["results"]]
        self.assertEqual(names({"search": "bergamot"}), ["Oud Minimaliste"])
        self.assertEqual(names({"category": self.floral.pk}), ["Golden Bloom"])
        self.assertEqual(names({"brand": "aurélia"}), ["Golden Bloom"])
        self.assertEqual(names({"min_price": 200, "ordering": "price"}), ["Golden Bloom", "Oud Minimaliste"])
        self.assertEqual(names({"ordering": "-sold"})[0], "Midnight Noir")
        self.assertEqual(names({"is_featured": "true"}), ["Oud Minimaliste"])

    def test_product_detail_with_branches(self):
        with self.assertNumQueries(2):  # product + branches prefetch (anonymous)
            data = self.client.get(reverse("v1:catalog:app-product-detail", args=[self.oud.pk])).json()
        self.assertEqual((data["branches"], data["image_urls"]), ([{"id": self.paris.pk, "name": "Place Vendôme", "city": "Paris"}], ["https://x/p.png"]))

    def test_reviews_require_delivered_purchase_and_award_points(self):
        url = reverse("v1:catalog:app-product-reviews", args=[self.oud.pk])
        with self.assertNumQueries(2):
            self.assertEqual(len(self.client.get(url).json()["results"]), 2)
        self.auth()
        self.assertEqual(self.client.post(url, {"rating": 5, "comment": "Lovely"}).status_code, 400)

        order = Order.objects.create(customer=self.customer, total=Decimal("240"), payment_method="card", status="delivered")
        OrderItem.objects.create(order=order, product=self.oud, product_name="Oud", sku="x", unit_price="240")
        self.assertEqual(self.client.post(url, {"rating": 5, "comment": "Lovely"}).status_code, 201)
        self.assertEqual(self.client.post(url, {"rating": 4}).status_code, 400)  # one review each
        entry = LoyaltyTransaction.objects.get(customer=self.customer)
        self.assertEqual((entry.reason, entry.points, entry.reference[:3]), ("review", 50, "RV-"))

    def test_saved_products(self):
        self.auth()
        url = reverse("v1:catalog:app-saved-product-list")
        for _ in range(2):
            self.assertEqual(self.client.post(url, {"product": self.bloom.pk}).status_code, 201)
        with self.assertNumQueries(3):
            saved = self.client.get(url).json()["results"]
        self.assertEqual([(p["name"], p["is_saved"]) for p in saved], [("Golden Bloom", True)])
        self.assertEqual(self.client.delete(reverse("v1:catalog:app-saved-product-detail", args=[self.bloom.pk])).status_code, 204)
        self.assertFalse(SavedProduct.objects.exists())

    def test_branches_search_and_nearby(self):
        url = reverse("v1:branches:app-branch-list")
        self.assertEqual([b["name"] for b in self.client.get(url, {"search": "london"}).json()["results"]], ["Mayfair"])
        nearby = [b["name"] for b in self.client.get(url, {"lat": 51.5, "lng": -0.1}).json()["results"]]
        self.assertEqual(nearby, ["Mayfair", "Place Vendôme"])
