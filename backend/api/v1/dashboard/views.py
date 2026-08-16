from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics import services
from apps.analytics.metrics import InvalidBranchError, InvalidDateRangeError


class DashboardView(APIView):
    def get(self, request):
        try:
            branch, date_range = services.resolve_context(request.query_params)
        except (InvalidBranchError, InvalidDateRangeError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(services.get_dashboard_metrics(date_range, branch))
