from unittest.mock import patch

from django.test import TestCase

from apps.ai.services import AIServiceError


class AIChatEndpointTests(TestCase):
    def test_missing_message_returns_400(self):
        resp = self.client.post("/api/v1/ai/chat/", data={}, content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_blank_message_returns_400(self):
        resp = self.client.post(
            "/api/v1/ai/chat/", data={"message": "   "}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    @patch("api.v1.ai.views.answer_question")
    def test_valid_question_returns_answer(self, mock_answer):
        mock_answer.return_value = {
            "answer": "Today's sales were AED 50.40 from 1 order.",
            "intent": "sales_summary",
            "period": {"start_date": "2026-08-16", "end_date": "2026-08-16", "branch": None},
        }
        resp = self.client.post(
            "/api/v1/ai/chat/", data={"message": "What were today's sales?"}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["intent"], "sales_summary")
        self.assertIn("AED 50.40", resp.data["answer"])

    @patch("api.v1.ai.views.answer_question")
    def test_ai_service_error_returns_503_without_exposing_internals(self, mock_answer):
        mock_answer.side_effect = AIServiceError("The AI Copilot isn't configured yet.")
        resp = self.client.post(
            "/api/v1/ai/chat/", data={"message": "What were today's sales?"}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 503)
        self.assertIn("error", resp.data)
        self.assertNotIn("Traceback", resp.data["error"])
