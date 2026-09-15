"""Demo customers, orders and loyalty history for reviewing the admin locally.

Uses existing products, branches and rewards. Safe to re-run: skips if demo
customers already exist.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.catalog.models import Product
from Apps.loyalty import services as loyalty
from Apps.loyalty.models import LoyaltyTransaction, Reward
from Apps.orders.models import Order, OrderItem, OrderStatusEvent

DOMAIN = "demo.madperfume.com"
CUSTOMERS = [
    ("Sophia Lauren", "+1 (555) 012-3456", "452 Fifth Avenue, Apt 12B\nNew York, NY 10018, USA"),
    ("Julian Vane", "+44 20 7946 0958", "22 Kensington Park Rd\nLondon W11 3BU, United Kingdom"),
    ("Amara Okafor", "+234 803 123 4567", "14 Admiralty Way, Lekki\nLagos, Nigeria"),
    ("Robert Chen", "+86 21 6123 4567", "88 Century Avenue\nShanghai 200120, China"),
    ("Marco Rossi", "+39 02 1234 5678", "Via della Spiga 5\n20121 Milan, Italy"),
    ("Julianne Moore", "+1 (555) 234-8901", "1224 Rue de Rivoli\n75001 Paris, France"),
    ("Layla Haddad", "+971 50 123 4567", "Downtown Boulevard 7\nDubai, UAE"),
]
FLOW = ["pending_payment", "paid", "processing", "shipped", "delivered"]


class Command(BaseCommand):
    help = "Creates demo customers, orders and loyalty transactions."

    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.filter(email__endswith=DOMAIN).exists():
            self.stdout.write("Demo data already present — nothing to do.")
            return
        products, branches = list(Product.objects.all()), list(Branch.objects.all())
        if not products or not branches:
            self.stderr.write("Add at least one product and one branch first.")
            return

        rng = random.Random(7)
        now = timezone.now()
        customers = []
        for i, (name, phone, address) in enumerate(CUSTOMERS):
            email = f"{name.split()[0].lower()}@{DOMAIN}"
            customer = User.objects.create_user(email=email, password=None, full_name=name, phone=phone, shipping_address=address)
            User.objects.filter(pk=customer.pk).update(created_at=now - timedelta(days=5 + i * 9))
            customers.append(customer)

        for n in range(14):
            customer = customers[n % len(customers)]
            placed = now - timedelta(days=40 - n * 3, hours=rng.randint(0, 8))
            if n % 5 == 4:  # in-store purchase
                amount = Decimal(rng.randrange(80, 900))
                order = Order.objects.create(customer=customer, channel="branch", branch=rng.choice(branches), status="in_store",
                                             subtotal=amount, total=amount, payment_method="in_store")
                self._stamp(order, ["in_store"], placed)
            else:
                picks = rng.sample(products, k=min(len(products), rng.randint(1, 3)))
                subtotal = Decimal("0")
                order = Order.objects.create(customer=customer, total=0, payment_method=rng.choice(["card", "debit", "cod"]),
                                             shipping_method="Express", shipping_address=customer.shipping_address,
                                             payment_reference=f"TXN_{88290100 + n}", card_last4="4242")
                for product in picks:
                    qty = rng.randint(1, 2)
                    OrderItem.objects.create(order=order, product=product, product_name=product.name, sku=product.sku,
                                             image_url=next((img["url"] for img in product.images if img), ""),
                                             unit_price=product.price, quantity=qty)
                    subtotal += product.price * qty
                shipping, tax = Decimal("15.00"), (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
                order.subtotal, order.shipping_fee, order.tax, order.total = subtotal, shipping, tax, subtotal + shipping + tax
                order.status = "cancelled" if n == 7 else FLOW[min(len(FLOW) - 1, (14 - n) // 2)]
                if order.payment_method == "cod":
                    order.payment_reference = order.card_last4 = ""
                order.save()
                steps = ["pending_payment", "cancelled"] if order.status == "cancelled" else FLOW[: FLOW.index(order.status) + 1]
                self._stamp(order, steps, placed)
            if order.status in ("delivered", "in_store"):
                entry = loyalty.earn_for_order(order)
                LoyaltyTransaction.objects.filter(pk=entry.pk).update(created_at=placed + timedelta(hours=2))

        # Long-standing clients: large past boutique purchases for tier variety.
        for customer, amount in zip(customers, [Decimal("16500"), Decimal("3100"), Decimal("8200"), Decimal("0"), Decimal("2700")]):
            if amount:
                placed = now - timedelta(days=200)
                order = Order.objects.create(customer=customer, channel="branch", branch=branches[-1], status="in_store",
                                             subtotal=amount, total=amount, payment_method="in_store")
                self._stamp(order, ["in_store"], placed)
                entry = loyalty.earn_for_order(order)
                LoyaltyTransaction.objects.filter(pk=entry.pk).update(created_at=placed + timedelta(hours=1))

        for reward, customer in zip(Reward.objects.order_by("points_required")[:2], customers):
            customer.refresh_from_db()
            if customer.points_balance >= reward.points_required:
                loyalty.redeem(customer, reward, channel="branch", branch=branches[0])

        self.stdout.write(self.style.SUCCESS(f"Created {len(customers)} customers and {Order.objects.count()} orders."))

    @staticmethod
    def _stamp(order, statuses, placed):
        Order.objects.filter(pk=order.pk).update(created_at=placed)
        for i, status in enumerate(statuses):
            event = OrderStatusEvent.objects.create(order=order, status=status)
            OrderStatusEvent.objects.filter(pk=event.pk).update(created_at=placed + timedelta(minutes=5 + i * 180 if i else 0))
