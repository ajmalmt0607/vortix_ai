import uuid
from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.core.pagination import StandardResultsPagination
from apps.orders.models import Order
from apps.orders.serializers import OrderDetailSerializer, OrderListSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        qs = Order.objects.select_related("branch", "customer").order_by("-ordered_at")
        params = self.request.query_params

        branch = params.get("branch")
        if branch:
            try:
                uuid.UUID(branch)
            except (ValueError, TypeError):
                raise ValidationError({"branch": "Invalid branch id."})
            qs = qs.filter(branch_id=branch)

        status_param = params.get("status")
        if status_param:
            status_value = status_param.upper()
            if status_value not in Order.OrderStatus.values:
                raise ValidationError({"status": f"Must be one of {Order.OrderStatus.values}."})
            qs = qs.filter(status=status_value)

        order_type = params.get("order_type")
        if order_type:
            order_type_value = order_type.upper()
            if order_type_value not in Order.OrderType.values:
                raise ValidationError({"order_type": f"Must be one of {Order.OrderType.values}."})
            qs = qs.filter(order_type=order_type_value)

        start_date = params.get("start_date")
        end_date = params.get("end_date")
        if start_date or end_date:
            if not (start_date and end_date):
                raise ValidationError("Both start_date and end_date must be provided together.")
            start = parse_date(start_date)
            end = parse_date(end_date)
            if not start or not end:
                raise ValidationError("Dates must be in YYYY-MM-DD format.")
            if start > end:
                raise ValidationError("start_date must not be after end_date.")
            tz = timezone.get_current_timezone()
            start_dt = timezone.make_aware(datetime.combine(start, time.min), tz)
            end_dt = timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min), tz)
            qs = qs.filter(ordered_at__gte=start_dt, ordered_at__lt=end_dt)

        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(order_number__icontains=search)
                | Q(customer__name__icontains=search)
                | Q(customer__phone__icontains=search)
            )

        return qs


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.select_related("branch", "customer").prefetch_related("items__product")
    lookup_field = "pk"
