from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.services import AIServiceError, answer_question


class AIChatView(APIView):
    def post(self, request):
        message = request.data.get("message")
        if not message or not str(message).strip():
            return Response({"error": "'message' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = answer_question(str(message))
        except AIServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(result)
