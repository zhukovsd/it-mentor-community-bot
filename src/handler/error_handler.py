import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.handler import util
from src.config import env

log = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_msg = f"Unexpected error occured: {context.error}"

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
