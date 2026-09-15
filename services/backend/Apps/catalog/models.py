from django.db import models


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
