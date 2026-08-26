import logging
from functools import wraps

from telegram.ext import CommandHandler, MessageHandler

from src.metrics.metric_definitions import telegram_command_usage_total

log = logging.getLogger(__name__)


def _get_metric_label(handler) -> str | None:
    if isinstance(handler, CommandHandler):
        if handler.commands:
            return next(iter(handler.commands))

    if isinstance(handler, MessageHandler):
        callback = getattr(handler, "callback", None)

        if callback:
            return callback.__name__

    return None


def _wrap_callback_with_metric(handler, command_label: str) -> None:
    original_callback = handler.callback

    @wraps(original_callback)
    async def wrapped_callback(update, context):
        final_label = command_label
        lang = ""

        if command_label == "search_interviews_with_question":
            text = (update.effective_message.text or "").lower()

            lang = "python" if "qp" in text else "java"
            final_label = f"{command_label}_{lang}"

        telegram_command_usage_total.labels(command=final_label).inc()

        await original_callback(update, context)

    handler.callback = wrapped_callback


def instrument_application(application) -> None:
    original_add_handler = application.add_handler

    def monitored_add_handler(handler, group: int = 0) -> None:
        command_label = _get_metric_label(handler)

        if command_label:
            _wrap_callback_with_metric(handler, command_label)
        else:
            log.debug(
                "Handler %s skipped (no metric label found)",
                type(handler).__name__,
            )

        original_add_handler(handler, group)

    application.add_handler = monitored_add_handler
