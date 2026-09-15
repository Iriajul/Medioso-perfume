from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    is_flagship = models.BooleanField(default=False)
    weekday_opens = models.TimeField(help_text="Monday – Saturday")
    weekday_closes = models.TimeField()
    sunday_opens = models.TimeField(help_text="Sunday & holidays")
    sunday_closes = models.TimeField()
    # For the mobile app's map and nearby-branch search.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    image_public_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "branches"

    def __str__(self):
        return self.name
