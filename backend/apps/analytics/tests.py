from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.analytics import services
from apps.analytics.metrics import DateRange, growth_percentage
from apps.branches.models import Branch
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product


class AnalyticsServicesTests(TestCase):
    """Uses hand-built fixtures (not the random demo generator) so totals are exact."""

    @classmethod
    def setUpTestData(cls):
        cls.branch_a = Branch.objects.create(name="Test Marina", code="TST-A", city="Dubai")
        cls.branch_b = Branch.objects.create(name="Test Downtown", code="TST-B", city="Dubai")

        category = Category.objects.create(name="Test Burgers")
        cls.burger = Product.objects.create(
            name="Test Burger", sku="TST-SKU-1", category=category,
            price=Decimal("30.00"), cost=Decimal("12.00"),
        )
        cls.fries = Product.objects.create(
            name="Test Fries", sku="TST-SKU-2", category=category,
            price=Decimal("15.00"), cost=Decimal("5.00"),
        )

        cls.today = timezone.localdate()

        # branch_a: 2 completed orders + 1 cancelled (must be excluded from all metrics).
        cls._make_order(cls.branch_a, "ORD-T001", Order.OrderStatus.COMPLETED, [(cls.burger, 1), (cls.fries, 1)])
        cls._make_order(cls.branch_a, "ORD-T002", Order.OrderStatus.COMPLETED, [(cls.burger, 2)])
        cls._make_order(cls.branch_a, "ORD-T003", Order.OrderStatus.CANCELLED, [(cls.burger, 5)])

        # branch_b: 1 completed order.
        cls._make_order(cls.branch_b, "ORD-T004", Order.OrderStatus.COMPLETED, [(cls.fries, 3)])

        cls.date_range = DateRange(start_date=cls.today, end_date=cls.today)

    @classmethod
    def _make_order(cls, branch, order_number, status, items):
        tz = timezone.get_current_timezone()
        ordered_at = timezone.make_aware(
            timezone.datetime.combine(cls.today, timezone.datetime.min.time()).replace(hour=12), tz
        )
        subtotal = sum(product.price * qty for product, qty in items)
        tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
        total = subtotal + tax
        order = Order.objects.create(
            branch=branch,
            order_number=order_number,
            order_type=Order.OrderType.DINE_IN,
            status=status,
            subtotal=subtotal,
            discount=Decimal("0.00"),
            tax=tax,
            total=total,
            ordered_at=ordered_at,
        )
        for product, qty in items:
            OrderItem.objects.create(
                order=order, product=product, quantity=qty, unit_price=product.price,
                discount=Decimal("0.00"), total=product.price * qty,
            )
        return order

    def test_sales_summary_excludes_cancelled_orders(self):
        summary = services.get_sales_summary(self.date_range)
        self.assertEqual(summary["orders"], 3)
        expected_revenue = (
            (self.burger.price + self.fries.price) * Decimal("1.05")
            + (self.burger.price * 2) * Decimal("1.05")
            + (self.fries.price * 3) * Decimal("1.05")
        ).quantize(Decimal("0.01"))
        self.assertAlmostEqual(float(summary["revenue"]), float(expected_revenue), delta=0.05)

    def test_top_products_ordering(self):
        top = services.get_top_products(self.date_range)
        names = [p["product_name"] for p in top]
        # Fries: 1+3=4 units, Burger: 1+2=3 units (cancelled order's 5 units excluded).
        self.assertEqual(names[0], "Test Fries")
        self.assertEqual(names[1], "Test Burger")

    def test_branch_totals_are_correct(self):
        performance = services.get_branch_performance(self.date_range)
        by_name = {row["branch_name"]: row for row in performance}
        self.assertEqual(by_name["Test Marina"]["orders"], 2)
        self.assertEqual(by_name["Test Downtown"]["orders"], 1)

    def test_order_type_totals_are_correct(self):
        breakdown = services.get_order_type_breakdown(self.date_range)
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0]["type"], "DINE_IN")
        self.assertEqual(breakdown[0]["orders"], 3)
        self.assertEqual(breakdown[0]["percentage"], 100.0)

    def test_product_combinations_are_returned(self):
        combos = services.get_product_combinations(self.date_range, min_orders_together=1)
        self.assertTrue(
            any({c["product_a"], c["product_b"]} == {"Test Burger", "Test Fries"} for c in combos)
        )

    def test_growth_percentage_handles_zero_previous(self):
        self.assertEqual(growth_percentage(100, 0), 0.0)

    def test_growth_percentage_calculates_correctly(self):
        self.assertEqual(growth_percentage(110, 100), 10.0)

    def test_previous_period_has_same_length(self):
        date_range = DateRange(start_date=self.today - timedelta(days=6), end_date=self.today)
        previous = date_range.previous_period()
        self.assertEqual(previous.days, date_range.days)
        self.assertEqual(previous.end_date, date_range.start_date - timedelta(days=1))
