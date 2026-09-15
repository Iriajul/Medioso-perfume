from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    class Channel(models.TextChoices):
        APP = "app", "Mobile App"
        BRANCH = "branch", "Physical Branch"

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        PAID = "paid", "Payment Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        IN_STORE = "in_store", "In Store Purchase"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Credit Card"
        DEBIT = "debit", "Debit Card"
        COD = "cod", "Cash on Delivery"
        IN_STORE = "in_store", "Paid In Store"

    ACTIVE_STATUSES = [Status.PENDING_PAYMENT, Status.PAID, Status.PROCESSING, Status.SHIPPED]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.APP)
    branch = models.ForeignKey("branches.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    shipping_method = models.CharField(max_length=50, blank=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    payment_reference = models.CharField(max_length=100, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True, help_text="App checkout retries with the same key return this order.")
    card_last4 = models.CharField(max_length=4, blank=True)

    shipping_name = models.CharField(max_length=255, blank=True)
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_phone = models.CharField(max_length=30, blank=True)
    billing_address = models.TextField(blank=True, help_text="Blank means same as shipping.")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
        help_text="Staff member who registered an in-store purchase.",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["customer", "idempotency_key"], condition=~models.Q(idempotency_key=""), name="one_order_per_idempotency_key"),
        ]

    def __str__(self):
        return self.number

    @property
    def number(self):
        return f"MAD-{self.pk:05d}"

    @property
    def estimated_delivery(self):
        return (self.created_at + timedelta(days=settings.DELIVERY_DAYS)).date()


class OrderItem(models.Model):
    """A line item. Product details are copied so history survives product edits."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    product_name = models.CharField(max_length=150)
    variant = models.CharField(max_length=100, blank=True, help_text='e.g. "100ml / Eau de Parfum"')
    sku = models.CharField(max_length=20)
    image_url = models.URLField(max_length=500, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class OrderStatusEvent(models.Model):
    """Status history for the order timeline."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="+")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_cart_product")]
