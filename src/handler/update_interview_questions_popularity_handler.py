import asyncio
import logging
from telegram import ChatMember, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config.env import QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS
from src.github import github_service
from src.handler import util


UPDATE_INTERVIEW_QUESTIONS_POPULARITY = "updatequestionspopularity"

log = logging.getLogger(__name__)


async def update_questions_popularity(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), "updatequestionspopularity command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), "updatequestionspopularity command should be used by user, it must not be None"
    assert (
        command_message is not None
    ), "updatequestionspopularity command cannot be None"

    async def reply_with_error(text: str) -> None:
        error_message = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_to_message_id=command_message.id,
        )
        await asyncio.sleep(10)
        _ = await context.bot.delete_messages(
            chat_id=chat.id,
            message_ids=[command_message.id, error_message.id],
        )
        return

    chat_member = await update.get_bot().get_chat_member(chat.id, chat_member.id)

    if not _is_allowed_user(chat_member):
        log.error(
            f"{UPDATE_INTERVIEW_QUESTIONS_POPULARITY} was called by not allowed user: {chat_member.user.id}-{chat_member.status}"
        )
        await reply_with_error("У вас нет прав на использование данной команды")
        return

    try:
        message = github_service.update_questions_popularity()

        _ = await context.bot.send_message(
            reply_to_message_id=command_message.id,
            chat_id=chat.id,
            text=util.escape_special_chars(message),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except Exception as e:
        await reply_with_error(str(e))


def _is_allowed_user(user: ChatMember) -> bool:
    allowed_user_ids = QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS.split(",")
    allowed_user_ids = list(map(int, allowed_user_ids))

    user_id = user.user.id

    if user_id in allowed_user_ids:
        return True

    return False
