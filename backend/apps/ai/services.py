"""AI Copilot orchestration: LLM tool-calling glue around the analytics services.

The LLM never touches the database directly. It only picks a tool, supplies
structured arguments, and explains the tool's already-computed result. All
numbers come from apps.analytics.services (via apps.ai.tools) — never from
the model itself.
"""

import json
import logging

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

from . import tools
from .prompts import SYSTEM_PROMPT, build_context_preamble

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 3

TOOL_INTENT_MAP = {
    "get_sales_summary": "sales_summary",
    "get_order_summary": "order_summary",
    "get_top_products": "top_products",
    "get_bottom_products": "bottom_products",
    "get_branch_performance": "branch_performance",
    "get_product_combinations": "product_combinations",
    "get_peak_hours": "peak_hours",
    "get_business_summary": "business_summary",
}


class AIServiceError(Exception):
    """Raised with a message that is safe to show directly to the user."""


def _get_client() -> OpenAI:
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise AIServiceError(
            "The AI Copilot isn't configured yet. Please add an OpenAI API key to enable it."
        )
    return OpenAI(api_key=api_key)


def _branch_names():
    from apps.branches.models import Branch

    return list(Branch.objects.filter(is_active=True).order_by("name").values_list("name", flat=True))


def _build_messages(message: str) -> list:
    today = timezone.localdate()
    context = build_context_preamble(today.isoformat(), today.strftime("%A"), _branch_names())
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context},
        {"role": "user", "content": message},
    ]


def _execute_tool_call(tool_call) -> dict:
    name = tool_call.function.name
    fn = tools.TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool '{name}'."}

    try:
        arguments = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        logger.warning("AI tool call %s had unparsable arguments: %r", name, tool_call.function.arguments)
        return {"error": "Could not parse tool arguments."}

    try:
        return fn(**arguments)
    except TypeError as exc:
        logger.warning("AI tool %s called with bad arguments %s: %s", name, arguments, exc)
        return {"error": "Invalid arguments for this request."}
    except Exception:
        logger.exception("AI tool %s raised an unexpected error", name)
        return {"error": "Something went wrong while retrieving that data."}


def answer_question(message: str) -> dict:
    message = (message or "").strip()
    if not message:
        raise AIServiceError("Please ask a question about your restaurant's performance.")

    client = _get_client()
    messages = _build_messages(message)

    last_tool_name = None
    last_tool_result = None

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=tools.TOOL_SCHEMAS,
                tool_choice="auto",
            )
        except Exception as exc:
            logger.exception("OpenAI API call failed")
            raise AIServiceError(
                "The AI Copilot is temporarily unavailable. Please try again shortly."
            ) from exc

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            answer = (assistant_message.content or "").strip()
            if not answer:
                answer = "I couldn't find enough data to answer that question."
            return {
                "answer": answer,
                "intent": TOOL_INTENT_MAP.get(last_tool_name, "general"),
                "period": (last_tool_result or {}).get("period"),
            }

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in assistant_message.tool_calls
                ],
            }
        )

        for tool_call in assistant_message.tool_calls:
            result = _execute_tool_call(tool_call)
            last_tool_name = tool_call.function.name
            last_tool_result = result
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                }
            )

    raise AIServiceError("I couldn't finish answering that question. Please try rephrasing it.")
