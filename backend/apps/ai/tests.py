import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.ai import tools as ai_tools
from apps.ai.services import AIServiceError, answer_question
from apps.branches.models import Branch
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product


class _FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class _FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = _FakeFunction(name, arguments)


class _FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class _FakeChoice:
    def __init__(self, message):
        self.message = message


class _FakeResponse:
    def __init__(self, message):
        self.choices = [_FakeChoice(message)]


def _tool_call_response(tool_name, arguments, call_id="call_1"):
    return _FakeResponse(_FakeMessage(tool_calls=[_FakeToolCall(call_id, tool_name, json.dumps(arguments))]))


def _final_response(text):
    return _FakeResponse(_FakeMessage(content=text, tool_calls=[]))


@override_settings(OPENAI_API_KEY="test-key", OPENAI_MODEL="gpt-4o-mini")
class AICopilotTests(TestCase):
    """The LLM is fully mocked — these verify the tool-dispatch/DB wiring, not OpenAI itself."""

    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name="Dubai Marina", code="AI-TST-A", city="Dubai")
        category = Category.objects.create(name="AI Test Category")
        cls.burger = Product.objects.create(
            name="Chicken Burger", sku="AI-SKU-1", category=category,
            price=Decimal("32.00"), cost=Decimal("14.00"),
        )
        cls.fries = Product.objects.create(
            name="Fries", sku="AI-SKU-2", category=category,
            price=Decimal("16.00"), cost=Decimal("5.00"),
        )

        cls.today = timezone.localdate()
        tz = timezone.get_current_timezone()
        ordered_at = timezone.make_aware(
            timezone.datetime.combine(cls.today, timezone.datetime.min.time()).replace(hour=13), tz
        )
        order = Order.objects.create(
            branch=cls.branch, order_number="ORD-AI-001", order_type=Order.OrderType.DINE_IN,
            status=Order.OrderStatus.COMPLETED, subtotal=Decimal("48.00"), discount=Decimal("0.00"),
            tax=Decimal("2.40"), total=Decimal("50.40"), ordered_at=ordered_at,
        )
        OrderItem.objects.create(
            order=order, product=cls.burger, quantity=1, unit_price=Decimal("32.00"),
            discount=Decimal("0.00"), total=Decimal("32.00"),
        )
        OrderItem.objects.create(
            order=order, product=cls.fries, quantity=1, unit_price=Decimal("16.00"),
            discount=Decimal("0.00"), total=Decimal("16.00"),
        )

    @patch("apps.ai.services.OpenAI")
    def test_sales_question_uses_sales_summary_tool(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _tool_call_response(
                "get_sales_summary", {"start_date": str(self.today), "end_date": str(self.today)}
            ),
            _final_response("Today's sales were AED 50.40 from 1 order."),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("What were today's sales?")

        self.assertEqual(result["intent"], "sales_summary")
        self.assertIn("50.40", result["answer"])
        first_call_kwargs = client.chat.completions.create.call_args_list[0].kwargs
        self.assertEqual(first_call_kwargs["tools"], ai_tools.TOOL_SCHEMAS)

    @patch("apps.ai.services.OpenAI")
    def test_product_question_uses_top_products_tool(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _tool_call_response("get_top_products", {"limit": 5}),
            _final_response("Chicken Burger is your best-selling item."),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("What sold the most?")
        self.assertEqual(result["intent"], "top_products")
        self.assertIn("Chicken Burger", result["answer"])

    @patch("apps.ai.services.OpenAI")
    def test_branch_question_uses_branch_performance_tool(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _tool_call_response("get_branch_performance", {}),
            _final_response("Dubai Marina is performing best."),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("Which branch performed best?")
        self.assertEqual(result["intent"], "branch_performance")

    @patch("apps.ai.services.OpenAI")
    def test_combination_question_uses_combinations_tool(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _tool_call_response("get_product_combinations", {"product_name": "Chicken Burger"}),
            _final_response("Customers often order Fries with Chicken Burger."),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("What do customers usually order with Chicken Burger?")
        self.assertEqual(result["intent"], "product_combinations")

    @patch("apps.ai.services.OpenAI")
    def test_invalid_branch_is_handled_gracefully(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _tool_call_response("get_sales_summary", {"branch_name": "Atlantis"}),
            _final_response("I couldn't find a branch called Atlantis."),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("What were sales at Atlantis?")
        self.assertIn("Atlantis", result["answer"])

        second_call_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
        tool_message = next(m for m in second_call_messages if m["role"] == "tool")
        self.assertIn("error", tool_message["content"])

    def test_missing_api_key_raises_clean_error(self):
        with override_settings(OPENAI_API_KEY=""):
            with self.assertRaises(AIServiceError):
                answer_question("What were today's sales?")

    @patch("apps.ai.services.OpenAI")
    def test_unsupported_question_returns_general_intent(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            _final_response(
                "VORTIX focuses on your restaurant's business data — try asking about sales, orders, or products."
            ),
        ]
        mock_openai_cls.return_value = client

        result = answer_question("What's the weather today?")
        self.assertEqual(result["intent"], "general")
        self.assertIn("VORTIX", result["answer"])

    @patch("apps.ai.services.OpenAI")
    def test_openai_api_error_raises_clean_service_error(self, mock_openai_cls):
        client = MagicMock()
        client.chat.completions.create.side_effect = RuntimeError("connection reset")
        mock_openai_cls.return_value = client

        with self.assertRaises(AIServiceError):
            answer_question("What were today's sales?")


class AIToolsTests(TestCase):
    """Direct tool-function tests, bypassing the LLM entirely."""

    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name="Dubai Marina", code="AI-TOOLS-A", city="Dubai")
        category = Category.objects.create(name="AI Tools Category")
        cls.product = Product.objects.create(
            name="Test Item", sku="AI-TOOLS-SKU", category=category,
            price=Decimal("20.00"), cost=Decimal("8.00"),
        )
        cls.today = timezone.localdate()
        tz = timezone.get_current_timezone()
        ordered_at = timezone.make_aware(
            timezone.datetime.combine(cls.today, timezone.datetime.min.time()).replace(hour=13), tz
        )
        order = Order.objects.create(
            branch=cls.branch, order_number="ORD-TOOLS-001", order_type=Order.OrderType.TAKEAWAY,
            status=Order.OrderStatus.COMPLETED, subtotal=Decimal("20.00"), discount=Decimal("0.00"),
            tax=Decimal("1.00"), total=Decimal("21.00"), ordered_at=ordered_at,
        )
        OrderItem.objects.create(
            order=order, product=cls.product, quantity=1, unit_price=Decimal("20.00"),
            discount=Decimal("0.00"), total=Decimal("20.00"),
        )

    def test_get_sales_summary_returns_expected_shape(self):
        result = ai_tools.get_sales_summary(start_date=str(self.today), end_date=str(self.today))
        self.assertEqual(result["summary"]["orders"], 1)
        self.assertEqual(float(result["summary"]["revenue"]), 21.00)

    def test_unknown_branch_name_returns_error_not_hallucination(self):
        result = ai_tools.get_sales_summary(branch_name="Nonexistent Place")
        self.assertIn("error", result)
        self.assertIn("Nonexistent Place", result["error"])

    def test_partial_branch_name_resolves(self):
        result = ai_tools.get_sales_summary(
            start_date=str(self.today), end_date=str(self.today), branch_name="Marina"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["period"]["branch"]["name"], "Dubai Marina")

    def test_invalid_date_returns_error(self):
        result = ai_tools.get_sales_summary(start_date="not-a-date", end_date="2026-08-16")
        self.assertIn("error", result)
