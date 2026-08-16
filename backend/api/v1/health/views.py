from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Confirms the API process is up and can reach the database."""

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return Response({"status": "ok", "service": "vortix-backend"})
