from django.core.validators import MinValueValidator
from django.db import models

from apps.branches.models import Branch
from apps.core.models import BaseModel
from apps.products.models import Product


class Customer(BaseModel):
    """Minimal synthetic demo customer record — no profiling fields."""

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(BaseModel):
    class OrderType(models.TextChoices):
        DINE_IN = "DINE_IN", "Dine In"
        TAKEAWAY = "TAKEAWAY", "Takeaway"
        DELIVERY = "DELIVERY", "Delivery"

    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="orders")
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    order_number = models.CharField(max_length=20, unique=True)
    order_type = models.CharField(
        max_length=20, choices=OrderType.choices, default=OrderType.DINE_IN
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True
    )

    # Currency: AED. Never store currency symbols in numeric fields.
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    ordered_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["branch", "ordered_at"]),
            models.Index(fields=["order_type"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(subtotal__gte=0), name="order_subtotal_gte_0"),
            models.CheckConstraint(check=models.Q(discount__gte=0), name="order_discount_gte_0"),
            models.CheckConstraint(check=models.Q(tax__gte=0), name="order_tax_gte_0"),
            models.CheckConstraint(check=models.Q(total__gte=0), name="order_total_gte_0"),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["order", "product"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name="orderitem_quantity_gt_0"),
            models.CheckConstraint(check=models.Q(unit_price__gte=0), name="orderitem_unit_price_gte_0"),
            models.CheckConstraint(check=models.Q(discount__gte=0), name="orderitem_discount_gte_0"),
            models.CheckConstraint(check=models.Q(total__gte=0), name="orderitem_total_gte_0"),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
