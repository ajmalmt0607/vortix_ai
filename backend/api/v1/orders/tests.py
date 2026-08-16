from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.branches.models import Branch
from apps.orders.models import Customer, Order, OrderItem
from apps.products.models import Category, Product


class OrdersAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch_a = Branch.objects.create(name="Orders Test A", code="ORD-TST-A", city="Dubai")
        cls.branch_b = Branch.objects.create(name="Orders Test B", code="ORD-TST-B", city="Dubai")
        category = Category.objects.create(name="Orders Test Category")
        cls.product = Product.objects.create(
            name="Orders Test Product", sku="ORD-TST-SKU", category=category,
            price=Decimal("40.00"), cost=Decimal("15.00"),
        )
        cls.customer = Customer.objects.create(name="Jane Doe", phone="+971500000000")

        tz = timezone.get_current_timezone()
        cls.today = timezone.localdate()

        cls.orders = []
        for i in range(25):
            branch = cls.branch_a if i % 2 == 0 else cls.branch_b
            status = Order.OrderStatus.COMPLETED if i % 5 != 0 else Order.OrderStatus.CANCELLED
            order_type = Order.OrderType.DINE_IN if i % 3 != 0 else Order.OrderType.DELIVERY
            ordered_at = timezone.make_aware(
                timezone.datetime.combine(cls.today, timezone.datetime.min.time()).replace(hour=12), tz
            ) - timedelta(days=i)
            order = Order.objects.create(
                branch=branch,
                customer=cls.customer if i == 0 else None,
                order_number=f"ORD-TEST-{100000 + i}",
                order_type=order_type,
                status=status,
                subtotal=Decimal("40.00"),
                discount=Decimal("0.00"),
                tax=Decimal("2.00"),
                total=Decimal("42.00"),
                ordered_at=ordered_at,
            )
            OrderItem.objects.create(
                order=order, product=cls.product, quantity=1, unit_price=Decimal("40.00"),
                discount=Decimal("0.00"), total=Decimal("40.00"),
            )
            cls.orders.append(order)

    def test_pagination_default_page_size(self):
        resp = self.client.get("/api/v1/orders/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 25)
        self.assertEqual(len(resp.data["results"]), 20)
        self.assertIsNotNone(resp.data["next"])

    def test_pagination_custom_page_size(self):
        resp = self.client.get("/api/v1/orders/?page_size=5")
        self.assertEqual(len(resp.data["results"]), 5)

    def test_pagination_max_page_size_capped(self):
        resp = self.client.get("/api/v1/orders/?page_size=1000")
        self.assertEqual(len(resp.data["results"]), 25)  # only 25 exist; cap is 100

    def test_branch_filter(self):
        resp = self.client.get(f"/api/v1/orders/?branch={self.branch_a.id}&page_size=100")
        self.assertTrue(all(r["branch"]["id"] == str(self.branch_a.id) for r in resp.data["results"]))
        self.assertGreater(resp.data["count"], 0)

    def test_date_filter(self):
        start = self.today - timedelta(days=2)
        resp = self.client.get(f"/api/v1/orders/?start_date={start}&end_date={self.today}")
        self.assertGreater(resp.data["count"], 0)
        self.assertLess(resp.data["count"], 25)

    def test_status_filter(self):
        resp = self.client.get("/api/v1/orders/?status=CANCELLED&page_size=100")
        self.assertGreater(resp.data["count"], 0)
        self.assertTrue(all(r["status"] == "CANCELLED" for r in resp.data["results"]))

    def test_order_type_filter(self):
        resp = self.client.get("/api/v1/orders/?order_type=DELIVERY&page_size=100")
        self.assertGreater(resp.data["count"], 0)
        self.assertTrue(all(r["order_type"] == "DELIVERY" for r in resp.data["results"]))

    def test_search_by_order_number(self):
        resp = self.client.get("/api/v1/orders/?search=ORD-TEST-100000")
        self.assertEqual(resp.data["count"], 1)

    def test_search_by_customer_name(self):
        resp = self.client.get("/api/v1/orders/?search=Jane")
        self.assertEqual(resp.data["count"], 1)

    def test_order_detail_returns_items(self):
        order = self.orders[0]
        resp = self.client.get(f"/api/v1/orders/{order.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["order_number"], order.order_number)
        self.assertEqual(len(resp.data["items"]), 1)

    def test_order_detail_404(self):
        resp = self.client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(resp.status_code, 404)

    def test_invalid_status_returns_400(self):
        resp = self.client.get("/api/v1/orders/?status=NOPE")
        self.assertEqual(resp.status_code, 400)

    def test_invalid_branch_id_returns_400(self):
        resp = self.client.get("/api/v1/orders/?branch=not-a-uuid")
        self.assertEqual(resp.status_code, 400)
