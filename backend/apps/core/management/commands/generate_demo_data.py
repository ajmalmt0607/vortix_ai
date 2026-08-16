import random
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from apps.branches.models import Branch
from apps.orders.models import Customer, Order, OrderItem
from apps.products.models import Category, Product

VAT_RATE = Decimal("0.05")  # UAE standard VAT
TWO_PLACES = Decimal("0.01")

# Fictional demo branches only — not real restaurant locations.
BRANCHES = [
    {"name": "Dubai Marina", "code": "DXB-MAR", "city": "Dubai", "performance": 1.30},
    {"name": "Downtown Dubai", "code": "DXB-DWN", "city": "Dubai", "performance": 1.00},
    {"name": "Jumeirah", "code": "DXB-JMR", "city": "Dubai", "performance": 0.75},
    {"name": "Abu Dhabi", "code": "AUH-CTY", "city": "Abu Dhabi", "performance": 1.00},
]

# (name, category, price AED, cost AED, popularity weight)
PRODUCTS = [
    ("Chicken Burger", "Burgers", "32.00", "14.00", 12),
    ("Beef Burger", "Burgers", "36.00", "16.00", 7),
    ("Double Beef Burger", "Burgers", "46.00", "21.00", 4),
    ("Chicken Wings", "Chicken", "28.00", "12.00", 10),
    ("Chicken Wrap", "Chicken", "24.00", "10.00", 6),
    ("Fries", "Sides", "16.00", "5.00", 11),
    ("Cheese Fries", "Sides", "20.00", "7.00", 5),
    ("Caesar Salad", "Salads", "26.00", "11.00", 2),
    ("Pasta Alfredo", "Pasta & Pizza", "34.00", "15.00", 4),
    ("Margherita Pizza", "Pasta & Pizza", "38.00", "16.00", 5),
    ("Cola", "Drinks", "8.00", "2.50", 11),
    ("Pepsi", "Drinks", "8.00", "2.50", 6),
    ("Water", "Drinks", "4.00", "1.00", 7),
    ("Lemonade", "Drinks", "12.00", "4.00", 4),
    ("Milkshake", "Drinks", "18.00", "7.00", 5),
    ("Chocolate Cake", "Desserts", "22.00", "9.00", 4),
]

CATEGORIES = ["Burgers", "Chicken", "Sides", "Salads", "Pasta & Pizza", "Drinks", "Desserts"]

# Signature combo forced together frequently, for "commonly ordered together" analysis later.
COMBO = ["Chicken Burger", "Fries", "Cola"]

ORDER_TYPE_WEIGHTS = [
    (Order.OrderType.DINE_IN, 50),
    (Order.OrderType.TAKEAWAY, 25),
    (Order.OrderType.DELIVERY, 25),
]

# Hour -> relative weight. Peaks at lunch (12-14) and dinner (19-22).
HOUR_WEIGHTS = {
    **{h: 1 for h in range(0, 11)},
    11: 4,
    12: 10,
    13: 10,
    14: 6,
    15: 2,
    16: 2,
    17: 3,
    18: 5,
    19: 9,
    20: 10,
    21: 9,
    22: 5,
    23: 2,
}

# UAE weekend (Friday/Saturday) slightly elevated demand. Monday=0 ... Sunday=6.
WEEKDAY_WEIGHTS = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.05, 4: 1.25, 5: 1.3, 6: 1.0}


def money(value) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = "Generate synthetic UAE restaurant demo data (branches, products, customers, orders)."

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=100)
        parser.add_argument("--orders", type=int, default=1000)
        parser.add_argument("--days", type=int, default=90)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        seed = options["seed"]
        random.seed(seed)
        fake = Faker()
        Faker.seed(seed)

        branches = self._create_branches()
        categories = self._create_categories()
        products = self._create_products(categories)
        customers = self._create_customers(options["customers"], fake)

        self.stdout.write("Clearing previously generated orders...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()

        self._generate_orders(
            branches=branches,
            products=products,
            customers=customers,
            order_count=options["orders"],
            days=options["days"],
        )

        self.stdout.write(self.style.SUCCESS("Demo data generation complete."))
        self.stdout.write(f"  Branches:   {Branch.objects.count()}")
        self.stdout.write(f"  Categories: {Category.objects.count()}")
        self.stdout.write(f"  Products:   {Product.objects.count()}")
        self.stdout.write(f"  Customers:  {Customer.objects.count()}")
        self.stdout.write(f"  Orders:     {Order.objects.count()}")
        self.stdout.write(f"  OrderItems: {OrderItem.objects.count()}")

    def _create_branches(self):
        branches = {}
        for data in BRANCHES:
            branch, _ = Branch.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "city": data["city"],
                    "address": f"{data['name']} Street, {data['city']}, UAE",
                    "phone": f"+9714{random.randint(1000000, 9999999)}",
                },
            )
            branches[data["code"]] = {"branch": branch, "performance": data["performance"]}
        return branches

    def _create_categories(self):
        categories = {}
        for name in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": f"{name} menu items"}
            )
            categories[name] = category
        return categories

    def _create_products(self, categories):
        products = {}
        for index, (name, category_name, price, cost, weight) in enumerate(PRODUCTS, start=1):
            product, _ = Product.objects.update_or_create(
                sku=f"SKU-{index:04d}",
                defaults={
                    "name": name,
                    "category": categories[category_name],
                    "price": money(price),
                    "cost": money(cost),
                },
            )
            products[name] = {"product": product, "weight": weight}
        return products

    def _create_customers(self, count, fake):
        existing = list(Customer.objects.all()[:count])
        if len(existing) >= count:
            return existing

        to_create = []
        for _ in range(count - len(existing)):
            to_create.append(
                Customer(
                    name=fake.name(),
                    phone=f"+9715{random.randint(10000000, 99999999)}",
                    email=fake.unique.email() if random.random() < 0.7 else None,
                )
            )
        Customer.objects.bulk_create(to_create)
        return list(Customer.objects.all()[:count])

    def _pick_branch(self, branches):
        codes = list(branches.keys())
        weights = [branches[c]["performance"] for c in codes]
        return branches[random.choices(codes, weights=weights, k=1)[0]]["branch"]

    def _pick_order_datetime(self, days):
        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        day_offset = random.randint(0, days - 1)
        order_date = today - timedelta(days=day_offset)

        weekday_weight = WEEKDAY_WEIGHTS[order_date.weekday()]
        # Re-roll the day a second time weighted by weekend boost, cheaply approximating
        # higher Friday/Saturday density without a full weighted date distribution.
        if random.random() > weekday_weight / 1.3:
            day_offset = random.randint(0, days - 1)
            order_date = today - timedelta(days=day_offset)

        hours = list(HOUR_WEIGHTS.keys())
        weights = list(HOUR_WEIGHTS.values())
        hour = random.choices(hours, weights=weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        naive = timezone.datetime.combine(order_date, timezone.datetime.min.time()).replace(
            hour=hour, minute=minute, second=second
        )
        return timezone.make_aware(naive, tz)

    def _pick_order_items(self, products):
        names = list(products.keys())
        weights = [products[n]["weight"] for n in names]

        chosen = []
        if random.random() < 0.35:
            chosen.extend(COMBO)

        extra_count = random.randint(0, 2) if chosen else random.randint(1, 4)
        pool = [n for n in names if n not in chosen]
        pool_weights = [products[n]["weight"] for n in pool]
        for _ in range(extra_count):
            if not pool:
                break
            pick = random.choices(pool, weights=pool_weights, k=1)[0]
            chosen.append(pick)
            idx = pool.index(pick)
            pool.pop(idx)
            pool_weights.pop(idx)

        if not chosen:
            chosen.append(random.choices(names, weights=weights, k=1)[0])

        return chosen

    def _order_status(self, ordered_at):
        age = timezone.now() - ordered_at
        if age < timedelta(hours=6):
            return random.choices(
                [Order.OrderStatus.PENDING, Order.OrderStatus.CONFIRMED, Order.OrderStatus.COMPLETED],
                weights=[20, 30, 50],
                k=1,
            )[0]
        return random.choices(
            [Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED],
            weights=[95, 5],
            k=1,
        )[0]

    @transaction.atomic
    def _generate_orders(self, branches, products, customers, order_count, days):
        self.stdout.write(f"Generating {order_count} orders over the last {days} days...")

        existing_max = Order.objects.count()
        start_number = 100001 + existing_max

        order_items_batch = []
        for i in range(order_count):
            order_number = f"ORD-{start_number + i}"
            ordered_at = self._pick_order_datetime(days)
            branch = self._pick_branch(branches)
            customer = random.choice(customers) if random.random() < 0.7 else None
            order_type = random.choices(
                [t for t, _ in ORDER_TYPE_WEIGHTS],
                weights=[w for _, w in ORDER_TYPE_WEIGHTS],
                k=1,
            )[0]

            item_names = self._pick_order_items(products)
            subtotal = Decimal("0.00")
            items_data = []
            for name in item_names:
                product = products[name]["product"]
                quantity = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
                unit_price = product.price
                item_discount = money(unit_price * quantity * Decimal("0.05")) if random.random() < 0.1 else Decimal("0.00")
                item_total = money(unit_price * quantity - item_discount)
                subtotal += item_total
                items_data.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "discount": item_discount,
                        "total": item_total,
                    }
                )

            order_discount = money(subtotal * Decimal("0.05")) if random.random() < 0.15 else Decimal("0.00")
            taxable = subtotal - order_discount
            tax = money(taxable * VAT_RATE)
            total = money(taxable + tax)

            order = Order.objects.create(
                branch=branch,
                customer=customer,
                order_number=order_number,
                order_type=order_type,
                status=self._order_status(ordered_at),
                subtotal=money(subtotal),
                discount=order_discount,
                tax=tax,
                total=total,
                ordered_at=ordered_at,
            )

            for item in items_data:
                order_items_batch.append(OrderItem(order=order, **item))

            if len(order_items_batch) >= 500:
                OrderItem.objects.bulk_create(order_items_batch)
                order_items_batch = []

        if order_items_batch:
            OrderItem.objects.bulk_create(order_items_batch)
