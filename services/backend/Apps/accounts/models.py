"""Identity models.

One User model for admins/staff (is_staff) and customers. Customer profile and
loyalty balance live on the same row so lists need no joins.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from Apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Platform user. Email is the login identifier."""

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    shipping_address = models.TextField(blank=True)

    # Loyalty, kept in sync by Apps.loyalty.services (never edited directly).
    points_balance = models.IntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
