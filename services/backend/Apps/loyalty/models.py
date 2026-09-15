from django.conf import settings
from django.db import models

TIER_CHOICES = [("silver", "Silver"), ("gold", "Gold"), ("platinum", "Platinum"), ("diamond", "Diamond")]


class Reward(models.Model):
    class Category(models.TextChoices):
        PHYSICAL_PRODUCT = "physical_product", "Physical Product"
        EXPERIENCE = "experience", "Experience"
        SERVICE = "service", "Service"

    class Eligibility(models.TextChoices):
        ALL = "all", "All Tiers"
        GOLD = "gold", "Gold Only"
        PLATINUM = "platinum", "Platinum Only"
        DIAMOND = "diamond", "Diamond Only"

    name = models.CharField(max_length=150)
    points_required = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=Category.choices)
    eligibility = models.CharField(max_length=10, choices=Eligibility.choices, default=Eligibility.ALL)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500)
    image_public_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class LoyaltyTransaction(models.Model):
    """Ledger entry. Every change to a customer's points balance is one row."""

    class Kind(models.TextChoices):
        EARNED = "earned", "Earned"
        REDEEMED = "redeemed", "Redeemed"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="loyalty_transactions")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    channel = models.CharField(max_length=10, choices=[("app", "Mobile App"), ("branch", "Physical Branch")])
    branch = models.ForeignKey("branches.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="loyalty_transactions")
    reward = models.ForeignKey(Reward, on_delete=models.SET_NULL, null=True, blank=True, related_name="redemptions")
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points = models.IntegerField(help_text="Positive when earned, negative when redeemed.")
    balance_after = models.IntegerField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # An order can only earn points once.
            models.UniqueConstraint(fields=["order"], condition=models.Q(kind="earned"), name="one_earn_per_order"),
        ]

    @property
    def reference(self):
        """Order / invoice number shown in transaction tables."""
        if self.order_id:
            return f"MAD-{self.order_id:05d}"
        return f"RD-{self.pk:05d}"
