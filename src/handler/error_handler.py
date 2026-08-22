import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.config import env
from src.handler import util
from src.metrics.metric_definitions import telegram_errors_total

log = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    exception_name = type(context.error).__name__ if context.error else "UnknownError"

    try:
        telegram_errors_total.labels(exception_type=exception_name).inc()
    except Exception as e:
        log.warning("Failed to increment error metric: %s", e)

    error_msg = f"Unexpected error occurred: {context.error}"

    log.error(error_msg)

    error_msg = util.escape_special_chars(error_msg)

    _ = await context.bot.send_message(chat_id=env.ERRORS_CHAT_ID, text=error_msg)

    if not isinstance(update, Update):
        return
    if update.effective_message is None:
        return

    _ = await update.effective_message.reply_markdown_v2(
        "Произошла непредвиденная ошибка"
    )
