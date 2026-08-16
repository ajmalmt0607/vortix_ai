from celery import shared_task


@shared_task
def ai_health_check():
    """Confirms the AI app is wired into the Celery worker.

    The Phase 4 chat endpoint runs synchronously; this is reserved for future
    async AI workflows (e.g. batched insight generation).
    """
    return "VORTIX AI Copilot task queue is working."
