from datetime import time
from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.common.testing import png
from Apps.loyalty import services as loyalty
from Apps.loyalty.models import LoyaltyTransaction, Reward
from Apps.orders.models import Order, OrderItem, OrderStatusEvent

HOURS = {"weekday_opens": time(10), "weekday_closes": time(21), "sunday_opens": time(11), "sunday_closes": time(19)}


class AdminApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        cls.paris = Branch.objects.create(name="Paris Flagship", address="a", phone="1", **HOURS)
        cls.julian = User.objects.create_user(email="julian@example.com", password="x", full_name="Julian Marc", phone="+1 555")
        cls.sophia = User.objects.create_user(email="sophia@example.com", password="x", full_name="Sophia Chen")
        for i, customer in enumerate([cls.julian, cls.sophia, cls.julian]):
            order = Order.objects.create(customer=customer, total=Decimal("100.00") * (i + 1), subtotal=Decimal("100.00") * (i + 1),
                                         payment_method="card", status="processing")
            for n in range(2):
                OrderItem.objects.create(order=order, product_name=f"Oud {n}", sku=f"MAD-00{n}", image_url=f"https://x/{n}.png", unit_price="50.00")
            OrderStatusEvent.objects.create(order=order, status="processing")

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")


class OrderApiTests(AdminApiTestCase):
    def test_list_with_stats(self):
        # auth + count + page (customer join) + stats aggregate
        with self.assertNumQueries(4):
            data = self.client.get(reverse("v1:orders:order-list")).json()

        self.assertEqual((data["count"], data["total_revenue"], data["active_orders"]), (3, "600.00", 3))
        self.assertEqual(data["results"][0]["customer_email"], "julian@example.com")

    def test_detail_no_n_plus_one(self):
        order = Order.objects.first()
        # auth + order (joins) + items + events
        with self.assertNumQueries(4):
            data = self.client.get(reverse("v1:orders:order-detail", args=[order.pk])).json()
        self.assertEqual((len(data["items"]), data["items"][0]["line_total"], data["customer"]["full_name"]), (2, "50.00", order.customer.full_name))

    def test_delivered_awards_points_once(self):
        order = Order.objects.get(total="200.00")
        url = reverse("v1:orders:order-update-status", args=[order.pk])
        for _ in range(2):
            response = self.client.post(url, {"status": "shipped"})
            response = self.client.post(url, {"status": "delivered"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([e["status"] for e in response.json()["events"]], ["processing", "shipped", "delivered", "shipped", "delivered"])
        self.sophia.refresh_from_db()
        self.assertEqual((self.sophia.points_balance, self.sophia.lifetime_points), (200, 200))
        self.assertEqual(LoyaltyTransaction.objects.filter(order=order).count(), 1)

    def test_invalid_status_rejected(self):
        order = Order.objects.first()
        response = self.client.post(reverse("v1:orders:order-update-status", args=[order.pk]), {"status": "in_store"})
        self.assertEqual(response.status_code, 400)

    def test_register_in_store_purchase(self):
        older = Order.objects.create(customer=self.sophia, channel="branch", branch=self.paris, status="in_store", total=10, payment_method="in_store")
        Order.objects.filter(pk=older.pk).update(created_at=older.created_at.replace(year=2020))
        payload = {"customer": self.julian.pk, "branch": self.paris.pk, "amount": "420.75", "notes": "Gift wrap"}
        response = self.client.post(reverse("v1:orders:order-register-in-store"), payload)

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual((response.json()["points"], response.json()["balance"]), (420, 420))
        entry = LoyaltyTransaction.objects.get()
        self.assertEqual((entry.channel, entry.branch, entry.purchase_amount, entry.balance_after, entry.created_by),
                         ("branch", self.paris, Decimal("420.75"), 420, self.admin))

        with self.assertNumQueries(2):
            recent = self.client.get(reverse("v1:orders:order-recent-in-store")).json()
        self.assertEqual((recent["points_per_dollar"], recent["results"][0]["customer_name"], recent["results"][0]["points"]), (1, "Julian Marc", 420))
        self.assertEqual(recent["results"][1]["customer_name"], "Sophia Chen")  # newest first


class CustomerApiTests(AdminApiTestCase):
    def test_list(self):
        with self.assertNumQueries(4):
            data = self.client.get(reverse("v1:accounts:customer-list")).json()
        self.assertEqual((data["count"], data["active_clients"]), (2, 2))
        self.assertEqual(data["results"][0]["tier"], "silver")

    def test_profile_no_n_plus_one(self):
        order = Order.objects.filter(customer=self.julian).first()
        loyalty.earn_for_order(order)
        # auth + customer + spend aggregate + orders + items + loyalty history
        with self.assertNumQueries(6):
            data = self.client.get(reverse("v1:accounts:customer-detail", args=[self.julian.pk])).json()

        self.assertEqual((data["lifetime_spend"], data["avg_order_value"]), ("400.00", "200.00"))
        self.assertEqual((len(data["orders"]), len(data["orders"][0]["images"])), (2, 2))
        self.assertEqual(data["loyalty_history"][0]["reference"], order.number)
        self.assertEqual((data["next_tier"], data["tier_progress"]), ("gold", int(order.total * 100 / 2500)))

    def test_lookup_by_email(self):
        self.assertEqual(self.client.get(reverse("v1:accounts:customer-lookup"), {"email": "JULIAN@example.com"}).json()["id"], self.julian.pk)
        self.assertEqual(self.client.get(reverse("v1:accounts:customer-lookup"), {"email": "admin@madperfume.com"}).status_code, 404)


class LoyaltyTests(AdminApiTestCase):
    def test_tiers(self):
        self.assertEqual([loyalty.tier_for(p) for p in (0, 2499, 2500, 7500, 20000)], ["silver", "silver", "gold", "platinum", "diamond"])
        self.assertEqual(loyalty.tier_progress(20000), (None, 100))

    def test_redeem_checks_balance(self):
        reward = Reward.objects.create(name="Gift Wrap", points_required=150, category="service", image_url="https://x/r.png", image_public_id="r/1")
        loyalty.earn_for_order(Order.objects.filter(customer=self.julian).first())  # +300
        entry = loyalty.redeem(self.julian, reward, channel="branch", branch=self.paris)
        self.assertEqual((entry.points, entry.balance_after), (-150, 150))
        with self.assertRaises(Exception):
            loyalty.redeem(self.julian, Reward(points_required=1000, pk=reward.pk), channel="app")
        self.julian.refresh_from_db()
        self.assertEqual((self.julian.points_balance, self.julian.lifetime_points), (150, 300))

    @patch("Apps.common.media.cloudinary.uploader.upload", return_value={"secure_url": "https://x/r.png", "public_id": "r/new"})
    def test_rewards_crud_and_redemption_stats(self, upload):
        payload = {"name": "Midnight Oud 50ml", "points_required": 1500, "category": "physical_product", "eligibility": "platinum",
                   "description": "Complimentary bottle", "image": png()}
        self.assertEqual(self.client.post(reverse("v1:loyalty:reward-list"), payload, format="multipart").status_code, 201)

        with self.assertNumQueries(3):
            data = self.client.get(reverse("v1:loyalty:reward-list")).json()
        self.assertEqual((data["total_redemptions"], data["results"][0]["eligibility"]), (0, "platinum"))
