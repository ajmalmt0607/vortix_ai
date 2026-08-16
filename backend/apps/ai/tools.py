"""Tool layer the LLM can call. Every tool wraps the existing analytics services —
no ORM/SQL logic lives here, only parameter resolution (branch name -> Branch,
date strings -> DateRange) and result shaping for the LLM.
"""

from apps.analytics import services
from apps.analytics.metrics import InvalidDateRangeError, resolve_date_range
from apps.branches.models import Branch

DEFAULT_TOP_N = 5
MAX_TOP_N = 20


def _resolve_branch(branch_name):
    """Returns (Branch|None, error_message|None). Never hallucinates a branch."""
    if not branch_name:
        return None, None
    matches = Branch.objects.filter(is_active=True, name__icontains=branch_name.strip())
    count = matches.count()
    if count == 0:
        return None, f"No branch found matching '{branch_name}'."
    if count > 1:
        exact = matches.filter(name__iexact=branch_name.strip())
        if exact.exists():
            return exact.first(), None
        names = ", ".join(matches.values_list("name", flat=True))
        return None, f"'{branch_name}' matches multiple branches ({names}). Please be more specific."
    return matches.first(), None


def _resolve_range(start_date, end_date):
    try:
        return resolve_date_range(start_date, end_date), None
    except InvalidDateRangeError as exc:
        return None, str(exc)


def _clamp_limit(limit):
    try:
        limit = int(limit) if limit is not None else DEFAULT_TOP_N
    except (TypeError, ValueError):
        limit = DEFAULT_TOP_N
    return max(1, min(limit, MAX_TOP_N))


def get_sales_summary(start_date=None, end_date=None, branch_name=None):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return {
        "period": services.build_period(date_range, branch),
        "summary": services.get_sales_summary(date_range, branch),
        "comparison": services.get_comparison(date_range, branch),
    }


def get_order_summary(start_date=None, end_date=None, branch_name=None):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    summary = services.get_sales_summary(date_range, branch)
    return {
        "period": services.build_period(date_range, branch),
        "orders": summary["orders"],
        "average_order_value": summary["average_order_value"],
        "order_types": services.get_order_type_breakdown(date_range, branch),
    }


def get_top_products(start_date=None, end_date=None, branch_name=None, limit=DEFAULT_TOP_N):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return {
        "period": services.build_period(date_range, branch),
        "top_products": services.get_top_products(date_range, branch, limit=_clamp_limit(limit)),
    }


def get_bottom_products(start_date=None, end_date=None, branch_name=None, limit=DEFAULT_TOP_N):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return {
        "period": services.build_period(date_range, branch),
        "bottom_products": services.get_bottom_products(date_range, branch, limit=_clamp_limit(limit)),
    }


def get_branch_performance(start_date=None, end_date=None, branch_name=None):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return {
        "period": services.build_period(date_range, branch),
        "branch_performance": services.get_branch_performance(date_range, branch),
    }


def get_product_combinations(
    start_date=None, end_date=None, branch_name=None, product_name=None, limit=DEFAULT_TOP_N
):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    limit = _clamp_limit(limit)

    # Pull a wider pool from the existing service, then filter in-memory for the
    # requested product — avoids adding a product filter to the analytics layer.
    combos = services.get_product_combinations(date_range, branch, limit=50, min_orders_together=2)
    if product_name:
        needle = product_name.strip().lower()
        combos = [
            c for c in combos if needle in c["product_a"].lower() or needle in c["product_b"].lower()
        ]
        if not combos:
            return {
                "period": services.build_period(date_range, branch),
                "combinations": [],
                "note": f"No strong combinations found involving '{product_name}' in this period.",
            }

    return {
        "period": services.build_period(date_range, branch),
        "combinations": combos[:limit],
    }


def get_peak_hours(start_date=None, end_date=None, branch_name=None):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return {
        "period": services.build_period(date_range, branch),
        "peak_hours": services.get_peak_hours(date_range, branch),
    }


def get_business_summary(start_date=None, end_date=None, branch_name=None):
    branch, error = _resolve_branch(branch_name)
    if error:
        return {"error": error}
    date_range, error = _resolve_range(start_date, end_date)
    if error:
        return {"error": error}
    return services.get_dashboard_metrics(date_range, branch)


TOOL_FUNCTIONS = {
    "get_sales_summary": get_sales_summary,
    "get_order_summary": get_order_summary,
    "get_top_products": get_top_products,
    "get_bottom_products": get_bottom_products,
    "get_branch_performance": get_branch_performance,
    "get_product_combinations": get_product_combinations,
    "get_peak_hours": get_peak_hours,
    "get_business_summary": get_business_summary,
}


def _date_branch_params():
    return {
        "start_date": {
            "type": ["string", "null"],
            "description": "Start date as YYYY-MM-DD (Asia/Dubai business date). Omit for the default recent period.",
        },
        "end_date": {
            "type": ["string", "null"],
            "description": "End date as YYYY-MM-DD (Asia/Dubai business date). Omit for the default recent period.",
        },
        "branch_name": {
            "type": ["string", "null"],
            "description": "Branch name or partial name (e.g. 'Marina'). Omit to include all branches.",
        },
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_summary",
            "description": (
                "Revenue, order count, average order value, discount, tax, currency, and growth "
                "vs the previous comparable period. Use for 'sales', 'revenue' questions."
            ),
            "parameters": {"type": "object", "properties": _date_branch_params(), "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_summary",
            "description": "Order counts and the breakdown of orders by type (dine-in, takeaway, delivery).",
            "parameters": {"type": "object", "properties": _date_branch_params(), "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_products",
            "description": "Best-selling products by quantity sold.",
            "parameters": {
                "type": "object",
                "properties": {
                    **_date_branch_params(),
                    "limit": {"type": "integer", "description": "How many products to return (default 5, max 20)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bottom_products",
            "description": "Worst-performing products by quantity sold — for identifying underperforming menu items.",
            "parameters": {
                "type": "object",
                "properties": {
                    **_date_branch_params(),
                    "limit": {"type": "integer", "description": "How many products to return (default 5, max 20)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_branch_performance",
            "description": "Revenue, orders, average order value and growth per branch.",
            "parameters": {"type": "object", "properties": _date_branch_params(), "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_combinations",
            "description": (
                "Which products are frequently ordered together. Pass product_name to only see "
                "combinations involving one specific product (e.g. 'what goes with Chicken Burger')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    **_date_branch_params(),
                    "product_name": {
                        "type": ["string", "null"],
                        "description": "Only return combinations that include this product.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "How many combinations to return (default 5, max 20).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_peak_hours",
            "description": "Order volume and revenue by hour of day — identifies the busiest times.",
            "parameters": {"type": "object", "properties": _date_branch_params(), "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_summary",
            "description": (
                "A complete overview: sales summary, comparison, trend, top/bottom products, branch "
                "performance and business insights. Use for broad 'how is my restaurant doing' questions."
            ),
            "parameters": {"type": "object", "properties": _date_branch_params(), "required": []},
        },
    },
]
