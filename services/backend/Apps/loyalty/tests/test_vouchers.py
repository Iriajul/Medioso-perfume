from decimal import Decimal

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.catalog.models import Category, Product
from Apps.loyalty import services as loyalty
from Apps.loyalty.models import LoyaltyTransaction, Reward
from Apps.notifications.models import UserNotification
from Apps.orders.models import Order

SHIPPING = {"shipping_name": "Julien", "shipping_address": "14 Rue de la Paix", "shipping_city": "Paris"}


class VoucherTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name="Paris Flagship", address="a", phone="1", weekday_opens="10:00",
                                           weekday_closes="20:00", sunday_opens="11:00", sunday_closes="19:00")
        cls.staff = User.objects.create_superuser(email="admin@madperfume.com", password="x", full_name="Admin")
        cls.customer = User.objects.create_user(email="julien@example.com", password="x", full_name="Julien")
        cls.other = User.objects.create_user(email="other@example.com", password="x", full_name="Other")
        category = Category.objects.create(name="Oriental", type="exotic", image_url="https://x/c.png", image_public_id="c")
        cls.product = Product.objects.create(name="Velvet Oud", category=category, price="200.00", stock=9,
                                             size="100ml", images=[{"url": "https://x/p.png", "public_id": "p"}])
        img = {"image_url": "https://x/r.png", "image_public_id": "r"}
        cls.voucher_reward = Reward.objects.create(name="$20 Voucher", points_required=400, category="service", discount_amount="20.00", **img)
        cls.gift = Reward.objects.create(name="Discovery Set", points_required=400, category="physical_product", **img)  # discount 0
        for user in (cls.customer, cls.other):
            order = Order.objects.create(customer=user, channel="branch", branch=cls.branch, total=1000,
                                         status="in_store", payment_method="in_store")
            loyalty.earn_for_order(order)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")

    def redeem(self, reward, user=None):
        return loyalty.redeem(user or self.customer, reward, channel="app")

    @staticmethod
    def first_error(response, field="voucher_code"):
        value = response.json()[field]
        return value[0] if isinstance(value, list) else value

    def checkout(self, **extra):
        self.client.post(reverse("v1:orders:app-cart-list"), {"product": self.product.pk, "quantity": 1})
        return self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod", **extra})

    def test_voucher_discounts_app_checkout_once(self):
        voucher = self.redeem(self.voucher_reward)
        self.assertEqual([v["voucher_code"] for v in self.client.get(reverse("v1:loyalty:app-redemptions"), {"usable": "true"}).json()["results"]],
                         [voucher.reference])

        data = self.checkout(voucher_code=voucher.reference).json()
        # $200 - $20 = $180, tax 8% on the discounted amount.
        self.assertEqual((data["subtotal"], data["discount"], data["tax"], data["total"]), ("200.00", "20.00", "14.40", "194.40"))

        voucher.refresh_from_db()
        self.assertEqual((voucher.fulfilled_at is not None, voucher.order_id), (True, data["id"]))
        self.assertEqual(self.first_error(self.checkout(voucher_code=voucher.reference)), "This voucher has already been used.")
        self.assertEqual(self.client.get(reverse("v1:loyalty:app-redemptions"), {"usable": "true"}).json()["count"], 0)

    def test_voucher_rejected_for_other_customers_and_for_collectable_rewards(self):
        theirs = self.redeem(self.voucher_reward, user=self.other)
        self.assertEqual(self.first_error(self.checkout(voucher_code=theirs.reference)), "This voucher code isn't valid for your account.")
        self.assertEqual(self.first_error(self.checkout(voucher_code="RD-99999")), "This voucher code isn't valid for your account.")
        gift = self.redeem(self.gift)
        self.assertEqual(self.first_error(self.checkout(voucher_code=gift.reference)),
                         "This reward is collected in a boutique, not used as a discount.")
        self.assertEqual(Order.objects.filter(channel="app").count(), 0)

    def test_voucher_discounts_in_store_purchase_and_points(self):
        voucher = self.redeem(self.voucher_reward)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.staff)}")
        response = self.client.post(reverse("v1:orders:order-register-in-store"), {
            "customer": self.customer.pk, "branch": self.branch.pk, "amount": "100.00", "voucher_code": voucher.reference})
        body = response.json()
        # Points follow what was actually paid: $80 x 3.
        self.assertEqual((body["discount"], body["amount_due"], body["points"]), ("20.00", "80.00", 240))
        voucher.refresh_from_db()
        self.assertTrue(voucher.fulfilled_at)

    def test_discount_never_exceeds_the_purchase(self):
        big = Reward.objects.create(name="$500 Voucher", points_required=400, category="service",
                                    discount_amount="500.00", image_url="https://x/r.png", image_public_id="r")
        data = self.checkout(voucher_code=self.redeem(big).reference).json()
        self.assertEqual((data["discount"], data["total"]), ("200.00", "0.00"))

    def test_admin_sees_voucher_as_used_and_cannot_collect_it(self):
        voucher = self.redeem(self.voucher_reward)
        code = voucher.reference
        order_id = self.checkout(voucher_code=code).json()["id"]
        voucher.refresh_from_db()
        self.assertEqual(voucher.reference, code)  # the code survives being spent
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.staff)}")
        row = next(r for r in self.client.get(reverse("v1:loyalty:redemption-list")).json()["results"] if r["id"] == voucher.pk)
        self.assertEqual((row["status"], row["used_on_order"], row["discount_amount"]), ("used", f"MAD-{order_id:05d}", "20.00"))
        self.assertEqual(self.client.post(reverse("v1:loyalty:redemption-collect", args=[voucher.pk])).status_code, 400)

    def test_redeeming_emails_the_code_and_notifies(self):
        url = reverse("v1:loyalty:app-reward-redeem", args=[self.voucher_reward.pk])
        with self.captureOnCommitCallbacks(execute=True):
            code = self.client.post(url).json()["voucher_code"]
        self.assertEqual((len(mail.outbox), mail.outbox[0].to), (1, ["julien@example.com"]))
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn(code, html)
        self.assertIn("off your next purchase", html)
        note = UserNotification.objects.filter(user=self.customer, category="rewards").first()
        self.assertIn(f"Use code {code} for $20.00 off", note.body)

    def test_collectable_reward_email_says_collect_in_boutique(self):
        with self.captureOnCommitCallbacks(execute=True):
            code = self.client.post(reverse("v1:loyalty:app-reward-redeem", args=[self.gift.pk])).json()["voucher_code"]
        self.assertIn("Present this code at any MAD boutique", mail.outbox[0].alternatives[0][0])
        self.assertIn(f"Present voucher {code} at any MAD boutique",
                      UserNotification.objects.filter(user=self.customer, category="rewards").first().body)

    def test_collectable_reward_still_marked_by_staff(self):
        gift = self.redeem(self.gift)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.staff)}")
        data = self.client.post(reverse("v1:loyalty:redemption-collect", args=[gift.pk]), {"branch": self.branch.pk}).json()
        self.assertEqual((data["status"], data["branch_name"]), ("collected", "Paris Flagship"))
