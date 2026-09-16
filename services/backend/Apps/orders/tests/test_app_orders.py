from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import stripe
from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User
from Apps.catalog.models import Category, Product
from Apps.loyalty.models import LoyaltyTransaction
from Apps.orders.models import CartItem, Order

SHIPPING = {"shipping_name": "Julien Beaumont", "shipping_address": "14 Rue de la Paix", "shipping_city": "Paris"}


class AppOrderTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(email="julien@example.com", password="x", full_name="Julien Beaumont", phone="+33123456789")
        cls.admin = User.objects.create_superuser(email="admin@madperfume.com", password="x", full_name="Admin")
        category = Category.objects.create(name="Oriental", type="exotic", image_url="https://x/c.png", image_public_id="c")
        img = [{"url": "https://x/p.png", "public_id": "p"}]
        cls.oud = Product.objects.create(name="Velvet Oud", category=category, price="240.00", stock=3, size="100ml", notes="Oud, Saffron", images=img)
        cls.mist = Product.objects.create(name="Bergamot Mist", category=category, price="165.00", stock=10, size="50ml", images=img)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")

    def add(self, product, quantity=1):
        return self.client.post(reverse("v1:orders:app-cart-list"), {"product": product.pk, "quantity": quantity})

    def test_cart_add_update_remove(self):
        self.assertEqual(self.add(self.oud).status_code, 201)
        self.add(self.oud)  # increments
        self.assertIn("quantity", self.add(self.oud, 2).json())  # 2 + 2 > 3 in stock
        self.add(self.mist)

        with self.assertNumQueries(2):  # auth + items with products
            cart = self.client.get(reverse("v1:orders:app-cart-list")).json()
        item = cart["items"][0]
        self.assertEqual((cart["items_count"], cart["subtotal"]), (3, "645.00"))
        self.assertEqual((item["variant"], item["category_name"]), ("100ml / Eau de Parfum", "Oriental"))

        mist = CartItem.objects.get(product=self.mist)
        self.assertEqual(self.client.patch(reverse("v1:orders:app-cart-detail", args=[mist.pk]), {"quantity": 4}).status_code, 200)
        self.assertEqual(self.client.delete(reverse("v1:orders:app-cart-detail", args=[mist.pk])).status_code, 204)

    def test_cod_checkout_creates_order_and_clears_cart(self):
        self.add(self.oud)
        self.add(self.mist)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"})

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual((len(mail.outbox), mail.outbox[0].to), (1, ["julien@example.com"]))
        self.assertIn("437.40", mail.outbox[0].alternatives[0][0])  # invoice total
        data = response.json()
        self.assertEqual((data["subtotal"], data["tax"], data["shipping_fee"], data["total"]), ("405.00", "32.40", "0.00", "437.40"))
        self.assertEqual((data["status"], [e["status"] for e in data["events"]], data["client_secret"]), ("processing", ["pending_payment", "processing"], None))
        self.assertEqual((data["shipping_phone"], len(data["items"])), ("+33123456789", 2))
        oud = next(i for i in data["items"] if i["product"] == self.oud.pk)
        self.assertEqual((oud["notes"], oud["variant"]), (["Oud", "Saffron"], "100ml / Eau de Parfum"))
        self.oud.refresh_from_db()
        self.assertEqual(self.oud.stock, 2)
        self.assertFalse(CartItem.objects.exists())

    def test_checkout_idempotency_key_returns_same_order(self):
        self.add(self.oud)
        url, headers = reverse("v1:orders:app-order-list"), {"HTTP_IDEMPOTENCY_KEY": "3f2c9a4e-checkout-1"}
        first = self.client.post(url, {**SHIPPING, "payment_method": "cod"}, **headers)
        retry = self.client.post(url, {**SHIPPING, "payment_method": "cod"}, **headers)  # cart is already empty
        self.assertEqual((first.status_code, retry.status_code, retry.json()["id"]), (201, 200, first.json()["id"]))
        self.assertEqual(Order.objects.count(), 1)

    def test_checkout_rejects_empty_cart_and_oversell(self):
        self.assertEqual(self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"}).status_code, 400)
        self.add(self.oud, 3)
        Product.objects.filter(pk=self.oud.pk).update(stock=1)  # sold in a boutique meanwhile
        response = self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    # Real SDK objects (not dicts), as Stripe returns them.
    @patch("Apps.orders.api.app.stripe.PaymentMethod.retrieve", return_value=stripe.PaymentMethod.construct_from({"id": "pm_1", "card": {"last4": "4242"}}, "sk_test"))
    @patch("Apps.orders.api.app.stripe.Webhook.construct_event")
    @patch("Apps.orders.api.app.stripe.PaymentIntent.create", return_value=SimpleNamespace(id="pi_123", client_secret="pi_123_secret"))
    def test_card_checkout_and_webhook(self, create_intent, construct_event, retrieve_method):
        self.add(self.oud)
        data = self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "card"}).json()
        self.assertEqual((data["status"], data["client_secret"]), ("pending_payment", "pi_123_secret"))
        self.assertEqual(create_intent.call_args.kwargs["amount"], 25920)  # $259.20 in cents
        self.assertEqual(create_intent.call_args.kwargs["idempotency_key"], f"order-{data['id']}-payment")
        self.assertEqual(len(mail.outbox), 0)  # invoice waits for the payment

        construct_event.return_value = stripe.Event.construct_from(
            {"id": "evt_1", "type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123", "object": "payment_intent", "payment_method": "pm_1"}}}, "sk_test")
        self.client.credentials()
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.client.post(reverse("v1:orders:stripe-webhook"), b"{}", content_type="application/json").status_code, 200)
            self.client.post(reverse("v1:orders:stripe-webhook"), b"{}", content_type="application/json")  # Stripe redelivery
        order = Order.objects.get()
        self.assertEqual((order.status, order.card_last4, len(mail.outbox)), ("paid", "4242", 1))

        construct_event.side_effect = stripe.SignatureVerificationError("bad", "sig")
        self.assertEqual(self.client.post(reverse("v1:orders:stripe-webhook"), b"{}", content_type="application/json").status_code, 400)

    def test_order_history_and_tracking(self):
        self.add(self.oud)
        self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"})
        other = User.objects.create_user(email="o@example.com", password="x", full_name="O")
        Order.objects.create(customer=other, total=1, payment_method="cod")

        with self.assertNumQueries(5):  # auth + count + page + items + events
            history = self.client.get(reverse("v1:orders:app-order-list")).json()
        self.assertEqual(history["count"], 1)
        order_id = history["results"][0]["id"]
        detail = self.client.get(reverse("v1:orders:app-order-detail", args=[order_id])).json()
        self.assertTrue(detail["estimated_delivery"])
        other_order = Order.objects.get(customer=other)
        self.assertEqual(self.client.get(reverse("v1:orders:app-order-detail", args=[other_order.pk])).status_code, 404)

    def test_delivery_awards_app_rate_and_cancel_restores_stock(self):
        self.add(self.oud, 2)
        order_id = self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"}).json()["id"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")
        self.client.post(reverse("v1:orders:order-update-status", args=[order_id]), {"status": "delivered"})
        self.assertEqual(LoyaltyTransaction.objects.get().points, int(Decimal("518.40") * 5))

        self.add_order_and_cancel()

    def add_order_and_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.customer)}")
        self.add(self.mist, 4)
        order_id = self.client.post(reverse("v1:orders:app-order-list"), {**SHIPPING, "payment_method": "cod"}).json()["id"]
        self.mist.refresh_from_db()
        self.assertEqual(self.mist.stock, 6)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin)}")
        self.client.post(reverse("v1:orders:order-update-status", args=[order_id]), {"status": "cancelled"})
        self.mist.refresh_from_db()
        self.assertEqual(self.mist.stock, 10)
