from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from catalog.models import Product


class Review(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True)
    is_moderated = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ("user", "product")

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"
