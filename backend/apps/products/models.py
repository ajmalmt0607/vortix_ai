from django.db import models

from apps.core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(BaseModel):
    """Currency for all monetary fields is AED."""

    name = models.CharField(max_length=150, db_index=True)
    sku = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "name"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="product_price_gte_0"),
            models.CheckConstraint(check=models.Q(cost__gte=0), name="product_cost_gte_0"),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
