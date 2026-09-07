import asyncio
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import env
from src.handler import util
from src.metrics.metric_definitions import telegram_errors_total

log = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    exception_name = "UnknownError"
    exception_traceback = "No traceback available"

    if context.error is not None:
        exception_name = type(context.error).__name__
        exception_traceback = "\n".join(
            traceback.format_exception(
                type(context.error), context.error, context.error.__traceback__
            )
        )

    try:
        telegram_errors_total.labels(exception_type=exception_name).inc()
    except Exception as e:
        log.warning("Failed to increment error metric: %s", e)

    log.error(f"Unexpected error occurred: {exception_name}\n{exception_traceback}")

    error_messages = util.compress_messages(
        util.chunk_string(
            f"Unexpected error occurred: {util.escape_special_chars(exception_name)}\n```\n{util.escape_special_chars(exception_traceback)}\n```"
        )
    )

    for message in error_messages:
        _ = await context.bot.send_message(
            chat_id=env.ERRORS_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        await asyncio.sleep(1)

    if not isinstance(update, Update):
        return
    if update.effective_message is None:
        return

    _ = await update.effective_message.reply_markdown_v2(
        "Произошла непредвиденная ошибка"
    )
