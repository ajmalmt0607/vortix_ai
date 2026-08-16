from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", include("api.v1.health.urls")),
    path("api/v1/dashboard/", include("api.v1.dashboard.urls")),
    path("api/v1/analytics/", include("api.v1.analytics.urls")),
    path("api/v1/orders/", include("api.v1.orders.urls")),
    path("api/v1/ai/", include("api.v1.ai.urls")),
]
