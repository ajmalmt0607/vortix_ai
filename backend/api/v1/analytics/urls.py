from django.urls import path

from .views import (
    BranchesAnalyticsView,
    CombinationsAnalyticsView,
    PeakHoursAnalyticsView,
    ProductsAnalyticsView,
    SalesAnalyticsView,
)

urlpatterns = [
    path("sales/", SalesAnalyticsView.as_view(), name="analytics-sales"),
    path("products/", ProductsAnalyticsView.as_view(), name="analytics-products"),
    path("branches/", BranchesAnalyticsView.as_view(), name="analytics-branches"),
    path("combinations/", CombinationsAnalyticsView.as_view(), name="analytics-combinations"),
    path("peak-hours/", PeakHoursAnalyticsView.as_view(), name="analytics-peak-hours"),
]
