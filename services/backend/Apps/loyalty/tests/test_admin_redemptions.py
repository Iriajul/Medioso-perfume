from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.loyalty import services as loyalty
from Apps.loyalty.models import Reward
from Apps.notifications.models import UserNotification
from Apps.orders.models import Order


class AdminRedemptionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name="Paris Flagship", address="a", phone="1",
                                           weekday_opens="10:00", weekday_closes="20:00",
                                           sunday_opens="11:00", sunday_closes="19:00")
        cls.staff = User.objects.create_user(email="staff@madperfume.com", password="x", full_name="Camille", is_staff=True, branch=cls.branch)
        cls.customer = User.objects.create_user(email="julien@example.com", password="x", full_name="Julien")
        cls.voucher_reward = Reward.objects.create(name="$20 Voucher", points_required=400, category="service",
                                                   image_url="https://x/r.png", image_public_id="r")
        order = Order.objects.create(customer=cls.customer, channel="branch", branch=cls.branch,
                                     total=1000, status="in_store", payment_method="in_store")
        loyalty.earn_for_order(order)
        cls.entry = loyalty.redeem(cls.customer, cls.voucher_reward, channel="app")

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.staff)}")

    def test_list_filter_and_search(self):
        url = reverse("v1:loyalty:redemption-list")
        with self.assertNumQueries(4):  # auth + count + page + pending count
            data = self.client.get(url).json()
        row = data["results"][0]
        self.assertEqual((row["voucher_code"], row["status"], row["points"], row["customer_name"]),
                         (f"RD-{self.entry.pk:05d}", "processing", 400, "Julien"))
        self.assertEqual(data["pending_count"], 1)
        self.assertEqual(self.client.get(url, {"status": "collected"}).json()["count"], 0)
        self.assertEqual(self.client.get(url, {"search": "julien@example.com"}).json()["count"], 1)
        self.assertEqual(self.client.get(url, {"code": f"RD-{self.entry.pk:05d}"}).json()["count"], 1)
        self.assertEqual(self.client.get(url, {"code": "RD-09999"}).json()["count"], 0)

    def test_collect_marks_voucher_and_notifies_customer(self):
        url = reverse("v1:loyalty:redemption-collect", args=[self.entry.pk])
        data = self.client.post(url).json()
        self.assertEqual((data["status"], data["collected_by"], data["branch_name"]), ("collected", "Camille", "Paris Flagship"))
        self.assertTrue(data["fulfilled_at"])
        self.assertTrue(UserNotification.objects.filter(user=self.customer, category="rewards", title__endswith="collected").exists())
        self.assertEqual(self.client.post(url).status_code, 400)  # already collected

    def test_head_office_can_name_the_boutique(self):
        admin = User.objects.create_superuser(email="hq@madperfume.com", password="x", full_name="HQ")  # no branch
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(admin)}")
        data = self.client.post(reverse("v1:loyalty:redemption-collect", args=[self.entry.pk]), {"branch": self.branch.pk}).json()
        self.assertEqual((data["status"], data["branch_name"], data["collected_by"]), ("collected", "Paris Flagship", "HQ"))

    def test_customers_cannot_see_or_collect(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")
        self.assertEqual(self.client.get(reverse("v1:loyalty:redemption-list")).status_code, 403)
        self.assertEqual(self.client.post(reverse("v1:loyalty:redemption-collect", args=[self.entry.pk])).status_code, 403)
