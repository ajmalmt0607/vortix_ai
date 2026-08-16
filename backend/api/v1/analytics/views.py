from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics import services
from apps.analytics.metrics import InvalidBranchError, InvalidDateRangeError


class BaseAnalyticsView(APIView):
    """Resolves branch/date-range params, then delegates payload building to a subclass."""

    def get(self, request):
        try:
            branch, date_range = services.resolve_context(request.query_params)
        except (InvalidBranchError, InvalidDateRangeError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.build_payload(date_range, branch))

    def build_payload(self, date_range, branch):
        raise NotImplementedError


class SalesAnalyticsView(BaseAnalyticsView):
    def build_payload(self, date_range, branch):
        return {
            "period": services.build_period(date_range, branch),
            "summary": services.get_sales_summary(date_range, branch),
            "comparison": services.get_comparison(date_range, branch),
            "sales_trend": services.get_sales_trend(date_range, branch),
        }


class ProductsAnalyticsView(BaseAnalyticsView):
    def build_payload(self, date_range, branch):
        return {
            "period": services.build_period(date_range, branch),
            "top_products": services.get_top_products(date_range, branch),
            "bottom_products": services.get_bottom_products(date_range, branch),
        }


class BranchesAnalyticsView(BaseAnalyticsView):
    def build_payload(self, date_range, branch):
        return {
            "period": services.build_period(date_range, branch),
            "branch_performance": services.get_branch_performance(date_range, branch),
        }


class CombinationsAnalyticsView(BaseAnalyticsView):
    def build_payload(self, date_range, branch):
        return {
            "period": services.build_period(date_range, branch),
            "combinations": services.get_product_combinations(date_range, branch),
        }


class PeakHoursAnalyticsView(BaseAnalyticsView):
    def build_payload(self, date_range, branch):
        return {
            "period": services.build_period(date_range, branch),
            "peak_hours": services.get_peak_hours(date_range, branch),
        }
