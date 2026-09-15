from django.db import models
from django.utils import timezone


class Category(models.Model):
    class Type(models.TextChoices):
        CLASSIC = "classic", "Classic"
        PREMIUM = "premium", "Premium"
        EXOTIC = "exotic", "Exotic"
        SEASONAL = "seasonal", "Seasonal"
        NICHE = "niche", "Niche"

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500)
    image_public_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    branches = models.ManyToManyField("branches.Branch", blank=True, related_name="products")
    # Up to 3 Cloudinary images: [{"url": ..., "public_id": ...}, ...] in slot order.
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def sku(self):
        return f"MAD-{self.pk:03d}"


class Banner(models.Model):
    title = models.CharField(max_length=150)
    image_url = models.URLField(max_length=500)
    image_public_id = models.CharField(max_length=255)
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_active = models.BooleanField(default=True, help_text="Whether the banner is live between its dates.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_on"]

    def __str__(self):
        return self.title

    @property
    def status(self):
        today = timezone.localdate()
        if not self.is_active:
            return "hidden"
        if today < self.starts_on:
            return "scheduled"
        return "ended" if today > self.ends_on else "active"
