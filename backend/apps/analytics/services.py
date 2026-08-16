"""Analytics business logic. Views must call these functions rather than
building ORM aggregations themselves.
"""

from collections import defaultdict
from decimal import Decimal
from itertools import combinations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour, TruncDate
from django.utils import timezone as dj_timezone

from apps.branches.models import Branch
from apps.orders.models import Order, OrderItem

from .metrics import (
    DateRange,
    InvalidBranchError,
    datetime_bounds,
    growth_percentage,
    resolve_date_range,
    round_money,
    safe_divide,
)

EXCLUDED_STATUS = Order.OrderStatus.CANCELLED


def resolve_context(query_params):
    """Parse `branch`/`start_date`/`end_date` query params into (Branch|None, DateRange)."""
    branch = None
    branch_param = query_params.get("branch")
    if branch_param:
        try:
            branch = Branch.objects.get(id=branch_param, is_active=True)
        except (Branch.DoesNotExist, ValueError, TypeError, DjangoValidationError):
            raise InvalidBranchError("Invalid or unknown branch.")

    date_range = resolve_date_range(query_params.get("start_date"), query_params.get("end_date"))
    return branch, date_range


def build_period(date_range: DateRange, branch=None) -> dict:
    return {
        "start_date": date_range.start_date.isoformat(),
        "end_date": date_range.end_date.isoformat(),
        "branch": {"id": str(branch.id), "name": branch.name} if branch else None,
    }


def _base_order_queryset(date_range: DateRange, branch=None):
    start_dt, end_dt = datetime_bounds(date_range)
    qs = Order.objects.filter(ordered_at__gte=start_dt, ordered_at__lt=end_dt).exclude(
        status=EXCLUDED_STATUS
    )
    if branch is not None:
        qs = qs.filter(branch=branch)
    return qs


def get_sales_summary(date_range: DateRange, branch=None) -> dict:
    agg = _base_order_queryset(date_range, branch).aggregate(
        revenue=Sum("total"), discount=Sum("discount"), tax=Sum("tax"), orders=Count("id")
    )
    revenue = agg["revenue"] or Decimal("0")
    orders = agg["orders"] or 0
    return {
        "revenue": round_money(revenue),
        "orders": orders,
        "average_order_value": safe_divide(revenue, orders),
        "discount": round_money(agg["discount"] or 0),
        "tax": round_money(agg["tax"] or 0),
        "currency": "AED",
    }


def get_comparison(date_range: DateRange, branch=None) -> dict:
    current = get_sales_summary(date_range, branch)
    previous = get_sales_summary(date_range.previous_period(), branch)
    return {
        "revenue_growth": growth_percentage(current["revenue"], previous["revenue"]),
        "orders_growth": growth_percentage(current["orders"], previous["orders"]),
        "aov_growth": growth_percentage(current["average_order_value"], previous["average_order_value"]),
    }


def get_sales_trend(date_range: DateRange, branch=None) -> list:
    tz = dj_timezone.get_current_timezone()
    rows = (
        _base_order_queryset(date_range, branch)
        .annotate(day=TruncDate("ordered_at", tzinfo=tz))
        .values("day")
        .annotate(revenue=Sum("total"), orders=Count("id"))
        .order_by("day")
    )
    return [
        {"date": row["day"].isoformat(), "revenue": round_money(row["revenue"] or 0), "orders": row["orders"]}
        for row in rows
    ]


def get_order_type_breakdown(date_range: DateRange, branch=None) -> list:
    rows = list(
        _base_order_queryset(date_range, branch)
        .values("order_type")
        .annotate(orders=Count("id"), revenue=Sum("total"))
        .order_by("-orders")
    )
    total_orders = sum(row["orders"] for row in rows)
    result = []
    for row in rows:
        pct = safe_divide(Decimal(row["orders"]) * 100, total_orders) if total_orders else Decimal("0.00")
        result.append(
            {
                "type": row["order_type"],
                "orders": row["orders"],
                "revenue": round_money(row["revenue"] or 0),
                "percentage": float(pct),
            }
        )
    return result


def _product_sales_queryset(date_range: DateRange, branch=None):
    start_dt, end_dt = datetime_bounds(date_range)
    qs = OrderItem.objects.filter(
        order__ordered_at__gte=start_dt, order__ordered_at__lt=end_dt
    ).exclude(order__status=EXCLUDED_STATUS)
    if branch is not None:
        qs = qs.filter(order__branch=branch)
    return qs.values("product_id", "product__name").annotate(quantity=Sum("quantity"), revenue=Sum("total"))


def _serialize_product_rows(rows) -> list:
    return [
        {
            "product_id": str(row["product_id"]),
            "product_name": row["product__name"],
            "quantity": row["quantity"],
            "revenue": round_money(row["revenue"] or 0),
        }
        for row in rows
    ]


def get_top_products(date_range: DateRange, branch=None, limit: int = 5) -> list:
    rows = _product_sales_queryset(date_range, branch).order_by("-quantity")[:limit]
    return _serialize_product_rows(rows)


def get_bottom_products(date_range: DateRange, branch=None, limit: int = 5) -> list:
    rows = _product_sales_queryset(date_range, branch).order_by("quantity")[:limit]
    return _serialize_product_rows(rows)


def get_branch_performance(date_range: DateRange, branch=None) -> list:
    start_dt, end_dt = datetime_bounds(date_range)
    prev_range = date_range.previous_period()
    prev_start_dt, prev_end_dt = datetime_bounds(prev_range)

    current_qs = Order.objects.exclude(status=EXCLUDED_STATUS).filter(
        ordered_at__gte=start_dt, ordered_at__lt=end_dt
    )
    previous_qs = Order.objects.exclude(status=EXCLUDED_STATUS).filter(
        ordered_at__gte=prev_start_dt, ordered_at__lt=prev_end_dt
    )
    if branch is not None:
        current_qs = current_qs.filter(branch=branch)
        previous_qs = previous_qs.filter(branch=branch)

    current_rows = {
        row["branch_id"]: row
        for row in current_qs.values("branch_id").annotate(revenue=Sum("total"), orders=Count("id"))
    }
    previous_revenue = {
        row["branch_id"]: row["revenue"] or Decimal("0")
        for row in previous_qs.values("branch_id").annotate(revenue=Sum("total"))
    }

    branches_qs = Branch.objects.filter(id=branch.id) if branch is not None else Branch.objects.filter(
        is_active=True
    )

    result = []
    for b in branches_qs:
        row = current_rows.get(b.id)
        revenue = round_money(row["revenue"] or 0) if row else Decimal("0.00")
        orders = row["orders"] if row else 0
        prev_revenue = round_money(previous_revenue.get(b.id, 0))
        result.append(
            {
                "branch_id": str(b.id),
                "branch_name": b.name,
                "revenue": revenue,
                "orders": orders,
                "average_order_value": safe_divide(revenue, orders),
                "growth_percentage": growth_percentage(revenue, prev_revenue),
            }
        )

    result.sort(key=lambda row: row["revenue"], reverse=True)
    return result


def get_product_combinations(
    date_range: DateRange, branch=None, limit: int = 5, min_orders_together: int = 2
) -> list:
    """Simple co-occurrence: how often two products appear in the same order."""
    order_qs = _base_order_queryset(date_range, branch)
    items = OrderItem.objects.filter(order__in=order_qs).values_list(
        "order_id", "product_id", "product__name"
    )

    order_products = defaultdict(set)
    product_names = {}
    for order_id, product_id, product_name in items:
        product_names[product_id] = product_name
        order_products[order_id].add(product_id)

    product_order_counts = defaultdict(int)
    pair_counts = defaultdict(int)
    for products in order_products.values():
        for product_id in products:
            product_order_counts[product_id] += 1
        for a, b in combinations(sorted(products), 2):
            pair_counts[(a, b)] += 1

    combos = []
    for (a, b), together in pair_counts.items():
        if together < min_orders_together:
            continue
        base = min(product_order_counts[a], product_order_counts[b])
        association_pct = safe_divide(Decimal(together) * 100, base) if base else Decimal("0.00")
        combos.append(
            {
                "product_a": product_names[a],
                "product_b": product_names[b],
                "orders_together": together,
                "association_percentage": float(association_pct),
            }
        )

    combos.sort(key=lambda combo: combo["orders_together"], reverse=True)
    return combos[:limit]


def get_peak_hours(date_range: DateRange, branch=None) -> list:
    tz = dj_timezone.get_current_timezone()
    rows = (
        _base_order_queryset(date_range, branch)
        .annotate(hour=ExtractHour("ordered_at", tzinfo=tz))
        .values("hour")
        .annotate(orders=Count("id"), revenue=Sum("total"))
        .order_by("hour")
    )
    return [
        {"hour": row["hour"], "orders": row["orders"], "revenue": round_money(row["revenue"] or 0)}
        for row in rows
    ]


def get_business_insights(
    date_range: DateRange,
    branch=None,
    comparison: dict | None = None,
    branch_performance: list | None = None,
    combinations_data: list | None = None,
) -> list:
    insights = []

    comparison = comparison if comparison is not None else get_comparison(date_range, branch)
    revenue_growth = comparison["revenue_growth"]
    if revenue_growth >= 10:
        insights.append(
            {
                "type": "POSITIVE",
                "severity": "LOW",
                "title": "Revenue is growing",
                "description": f"Revenue increased by {revenue_growth}% compared with the previous period.",
            }
        )
    elif revenue_growth <= -10:
        insights.append(
            {
                "type": "WARNING",
                "severity": "HIGH",
                "title": "Revenue declined",
                "description": f"Revenue decreased by {abs(revenue_growth)}% compared with the previous period.",
            }
        )

    combinations_data = (
        combinations_data
        if combinations_data is not None
        else get_product_combinations(date_range, branch, limit=1, min_orders_together=5)
    )
    if combinations_data:
        top = combinations_data[0]
        if top["association_percentage"] >= 50:
            insights.append(
                {
                    "type": "OPPORTUNITY",
                    "severity": "MEDIUM",
                    "title": "Strong product combination detected",
                    "description": f"{top['product_a']} and {top['product_b']} are frequently ordered together.",
                }
            )

    if branch is None:
        branch_performance = (
            branch_performance if branch_performance is not None else get_branch_performance(date_range)
        )
        for row in branch_performance:
            if row["growth_percentage"] <= -10:
                insights.append(
                    {
                        "type": "WARNING",
                        "severity": "HIGH",
                        "title": "Branch performance needs attention",
                        "description": (
                            f"{row['branch_name']} revenue decreased by "
                            f"{abs(row['growth_percentage'])}% compared with the previous period."
                        ),
                    }
                )

    return insights


def get_dashboard_metrics(date_range: DateRange, branch=None) -> dict:
    comparison = get_comparison(date_range, branch)
    branch_performance = get_branch_performance(date_range, branch)
    combinations_data = get_product_combinations(date_range, branch, limit=5, min_orders_together=2)

    return {
        "period": build_period(date_range, branch),
        "summary": get_sales_summary(date_range, branch),
        "comparison": comparison,
        "sales_trend": get_sales_trend(date_range, branch),
        "order_types": get_order_type_breakdown(date_range, branch),
        "top_products": get_top_products(date_range, branch),
        "bottom_products": get_bottom_products(date_range, branch),
        "branch_performance": branch_performance,
        "insights": get_business_insights(
            date_range,
            branch,
            comparison=comparison,
            branch_performance=branch_performance,
            combinations_data=combinations_data[:1],
        ),
    }
