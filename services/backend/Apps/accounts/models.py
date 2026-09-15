"""Identity models.

The custom User is defined up-front because swapping AUTH_USER_MODEL after the
first migration is painful. Customer profile, roles (customer / branch staff),
addresses and loyalty fields are added with their features.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from Apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Platform user. Email is the login identifier."""

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

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
