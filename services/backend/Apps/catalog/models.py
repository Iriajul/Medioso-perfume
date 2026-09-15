from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
    class Concentration(models.TextChoices):
        EAU_DE_PARFUM = "eau_de_parfum", "Eau de Parfum"
        EAU_DE_TOILETTE = "eau_de_toilette", "Eau de Toilette"
        EXTRAIT = "extrait_de_parfum", "Extrait de Parfum"
        COLOGNE = "cologne", "Cologne"
        PERFUME_OIL = "perfume_oil", "Perfume Oil"
        HOME = "home_fragrance", "Home Fragrance"

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, default="MAD PERFUME")
    concentration = models.CharField(max_length=20, choices=Concentration.choices, default=Concentration.EAU_DE_PARFUM)
    size = models.CharField(max_length=30, blank=True, help_text='e.g. "100ml" or "300g"')
    notes = models.CharField(max_length=255, blank=True, help_text="Comma-separated scent notes, e.g. Oud, Bergamot, White Musk")
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

    @property
    def notes_list(self):
        return [n.strip() for n in self.notes.split(",") if n.strip()]


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


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["product", "user"], name="one_review_per_product")]


class SavedProduct(models.Model):
    """Customer wishlist ("Saved Items")."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_saved_product")]
