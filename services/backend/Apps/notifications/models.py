from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A broadcast to customers. Push delivery (FCM) runs once the mobile app registers device tokens."""

    class Audience(models.TextChoices):
        ALL = "all", "All Customers"
        SILVER = "silver", "Silver Members"
        GOLD = "gold", "Gold Members"
        PLATINUM = "platinum", "Platinum Members"
        DIAMOND = "diamond", "Diamond Members"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"

    title = models.CharField(max_length=150)
    body = models.TextField()
    audience = models.CharField(max_length=10, choices=Audience.choices, default=Audience.ALL)
    recipients_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    """One customer's inbox entry: broadcast offers, loyalty events and order updates."""

    class Category(models.TextChoices):
        OFFERS = "offers", "Offers & Curations"
        REWARDS = "rewards", "Loyalty & Rewards"
        ORDERS = "orders", "Order Status"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    category = models.CharField(max_length=10, choices=Category.choices)
    title = models.CharField(max_length=150)
    body = models.TextField()
    broadcast = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True, related_name="deliveries")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]
