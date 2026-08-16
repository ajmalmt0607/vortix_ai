from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.branches.models import Branch
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product


class DashboardAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name="API Test Branch", code="API-1", city="Dubai")
        category = Category.objects.create(name="API Test Category")
        cls.product = Product.objects.create(
            name="API Test Product", sku="API-SKU-1", category=category,
            price=Decimal("50.00"), cost=Decimal("20.00"),
        )

        cls.today = timezone.localdate()
        tz = timezone.get_current_timezone()
        ordered_at = timezone.make_aware(
            timezone.datetime.combine(cls.today, timezone.datetime.min.time()).replace(hour=13), tz
        )
        order = Order.objects.create(
            branch=cls.branch, order_number="ORD-API-001", order_type=Order.OrderType.TAKEAWAY,
            status=Order.OrderStatus.COMPLETED, subtotal=Decimal("50.00"), discount=Decimal("0.00"),
            tax=Decimal("2.50"), total=Decimal("52.50"), ordered_at=ordered_at,
        )
        OrderItem.objects.create(
            order=order, product=cls.product, quantity=1, unit_price=Decimal("50.00"),
            discount=Decimal("0.00"), total=Decimal("50.00"),
        )

    def test_dashboard_returns_200(self):
        resp = self.client.get("/api/v1/dashboard/")
        self.assertEqual(resp.status_code, 200)
        for key in [
            "period", "summary", "comparison", "sales_trend", "order_types",
            "top_products", "bottom_products", "branch_performance", "insights",
        ]:
            self.assertIn(key, resp.data)

    def test_dashboard_correct_revenue_and_orders(self):
        resp = self.client.get(f"/api/v1/dashboard/?start_date={self.today}&end_date={self.today}")
        self.assertEqual(resp.data["summary"]["orders"], 1)
        self.assertEqual(float(resp.data["summary"]["revenue"]), 52.50)

    def test_dashboard_handles_empty_date_range(self):
        past_day = self.today.replace(year=self.today.year - 1)
        resp = self.client.get(f"/api/v1/dashboard/?start_date={past_day}&end_date={past_day}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["summary"]["orders"], 0)
        self.assertEqual(float(resp.data["summary"]["revenue"]), 0.0)

    def test_dashboard_branch_filtering(self):
        resp = self.client.get(f"/api/v1/dashboard/?branch={self.branch.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["period"]["branch"]["id"], str(self.branch.id))
        self.assertEqual(len(resp.data["branch_performance"]), 1)

    def test_dashboard_invalid_dates(self):
        resp = self.client.get("/api/v1/dashboard/?start_date=bad&end_date=2026-08-16")
        self.assertEqual(resp.status_code, 400)

    def test_dashboard_start_after_end(self):
        resp = self.client.get("/api/v1/dashboard/?start_date=2026-08-16&end_date=2026-08-01")
        self.assertEqual(resp.status_code, 400)

    def test_dashboard_invalid_branch(self):
        resp = self.client.get("/api/v1/dashboard/?branch=not-a-uuid")
        self.assertEqual(resp.status_code, 400)
