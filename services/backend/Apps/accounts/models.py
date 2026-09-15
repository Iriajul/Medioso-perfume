"""Identity models.

One User model for admins/staff (is_staff) and customers. Customer profile and
loyalty balance live on the same row so lists need no joins.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from Apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Platform user. Email is the login identifier."""

    class StaffRole(models.TextChoices):
        BOUTIQUE_MANAGER = "boutique_manager", "Boutique Manager"
        MASTER_NOSE = "master_nose", "Master Nose"
        SENIOR_ADVISOR = "senior_advisor", "Senior Advisor"
        SALES_CONSULTANT = "sales_consultant", "Sales Consultant"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    avatar_public_id = models.CharField(max_length=255, blank=True)
    shipping_address = models.TextField(blank=True)

    # Loyalty, kept in sync by Apps.loyalty.services (never edited directly).
    points_balance = models.IntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Staff directory (is_staff accounts that are not superusers).
    branch = models.ForeignKey("branches.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="staff")
    job_title = models.CharField(max_length=30, choices=StaffRole.choices, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    # App preferences.
    language = models.CharField(max_length=2, choices=[("en", "English"), ("ar", "Arabic"), ("he", "Hebrew")], default="en")
    push_enabled = models.BooleanField(default=True)
    notify_collections = models.BooleanField(default=True)
    notify_rewards = models.BooleanField(default=True)
    notify_orders = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # Phone is a login identifier in the app, so it must be unique when set.
            models.UniqueConstraint(fields=["phone"], condition=~models.Q(phone=""), name="unique_phone_when_set"),
        ]

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        super().set_password(raw_password)
        if raw_password is not None:
            self.password_changed_at = timezone.now()


class PasswordResetCode(models.Model):
    """6-digit code emailed for the app's password reset (stored hashed)."""

    MAX_ATTEMPTS = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    code_hash = models.CharField(max_length=128)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class DeviceToken(models.Model):
    """FCM registration token for push notifications."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="device_tokens")
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, choices=[("ios", "iOS"), ("android", "Android")])
    created_at = models.DateTimeField(auto_now_add=True)
