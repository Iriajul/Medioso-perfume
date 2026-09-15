from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.loyalty import services as loyalty
from Apps.loyalty.models import Reward
from Apps.notifications.models import UserNotification
from Apps.orders.models import Order

IMG = {"image_url": "https://x/r.png", "image_public_id": "r"}


class AppLoyaltyTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(email="julien@example.com", password="x", full_name="Julien")
        cls.admin = User.objects.create_superuser(email="admin@madperfume.com", password="x", full_name="Admin")
        cls.branch = Branch.objects.create(name="Paris Flagship", address="a", phone="1", weekday_opens="10:00", weekday_closes="20:00", sunday_opens="11:00", sunday_closes="19:00")
        cls.voucher = Reward.objects.create(name="$20 Voucher", points_required=400, category="service", **IMG)
        cls.reserve = Reward.objects.create(name="Private Reserve", points_required=1000, category="physical_product", eligibility="platinum", **IMG)
        order = Order.objects.create(customer=cls.customer, channel="branch", branch=cls.branch, total=1000, status="in_store", payment_method="in_store")
        loyalty.earn_for_order(order)  # 3000 points → gold

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")

    def test_summary_and_history(self):
        with self.assertNumQueries(2):  # auth + recent activity with joins
            data = self.client.get(reverse("v1:loyalty:app-loyalty")).json()
        self.assertEqual((data["points_balance"], data["tier"], data["next_tier"], data["points_to_next_tier"]), (3000, "gold", "platinum", 4500))
        self.assertEqual((data["recent_activity"][0]["title"], data["earn_rates"]["app"]), ("Purchase: Paris Flagship", 5))
        # Reaching gold dropped a loyalty notification in the inbox.
        self.assertTrue(UserNotification.objects.filter(user=self.customer, title="Gold Status Achievement").exists())

        url = reverse("v1:loyalty:app-loyalty-transactions")
        self.assertEqual(self.client.get(url, {"channel": "branch"}).json()["count"], 1)
        self.assertEqual(self.client.get(url, {"kind": "redeemed"}).json()["count"], 0)

    def test_redeem_reward_checks_points_and_tier(self):
        rewards = {r["name"]: r["can_redeem"] for r in self.client.get(reverse("v1:loyalty:app-reward-list")).json()}
        self.assertEqual(rewards, {"$20 Voucher": True, "Private Reserve": False})  # platinum only
        self.assertEqual(self.client.post(reverse("v1:loyalty:app-reward-redeem", args=[self.reserve.pk])).status_code, 400)

        response = self.client.post(reverse("v1:loyalty:app-reward-redeem", args=[self.voucher.pk]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual((response.json()["status"], response.json()["points"], response.json()["voucher_code"][:3]), ("processing", 400, "RD-"))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.points_balance, 2600)

        with self.assertNumQueries(3):  # auth + count + page with reward
            redeemed = self.client.get(reverse("v1:loyalty:app-redemptions")).json()["results"]
        self.assertEqual([r["name"] for r in redeemed], ["$20 Voucher"])

    def test_inbox_broadcast_orders_and_read_state(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")
        self.client.post(reverse("v1:notifications:notification-list"), {"title": "Private Sale", "body": "20% off", "audience": "gold"})
        app_order = Order.objects.create(customer=self.customer, total=100, payment_method="cod", status="processing")
        self.client.post(reverse("v1:orders:order-update-status", args=[app_order.pk]), {"status": "shipped"})

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")
        url = reverse("v1:notifications:app-notification-list")
        with self.assertNumQueries(3):
            inbox = self.client.get(url).json()["results"]
        self.assertEqual([n["category"] for n in inbox], ["orders", "offers", "rewards"])
        self.assertEqual(inbox[0]["order_number"], app_order.number)
        self.assertEqual(self.client.get(url, {"category": "offers"}).json()["results"][0]["title"], "Private Sale")

        self.client.patch(reverse("v1:notifications:app-notification-detail", args=[inbox[0]["id"]]), {"is_read": True})
        self.assertEqual(self.client.get(reverse("v1:notifications:app-notification-unread-count")).json()["unread"], 2)
        self.client.post(reverse("v1:notifications:app-notification-read-all"))
        self.assertEqual(self.client.get(reverse("v1:notifications:app-notification-unread-count")).json()["unread"], 0)
