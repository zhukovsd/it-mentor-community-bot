import logging
import os
import asyncio
from time import sleep
from telegram import ChatMember, Message, Update
from repository import find_reply_by_language_and_project
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

ADD_PROJECT_COMMAND_NAME = "addproject"
PROJECT_NAMES = [
    "hangman",
    "simulation",
    "currency-exchange",
    "tennis-scoreboard",
    "weather-viewer",
    "cloud-file-storage",
    "task-tracker",
]

log = logging.getLogger(__name__)


async def add_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = await update.get_bot().get_chat_member(chat_id, user_id)

    if not is_admin(user) and not is_allowed_user(user):
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called by not admin user: {user.user.id}-{user.status}"
        )
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text="У вас нет прав на использование данной команды",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    if not is_reply(update.effective_message):
        log.error(f"{ADD_PROJECT_COMMAND_NAME} was called outside of reply")
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Сделайте реплай на сообщение со ссылкой на проект",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    command_text = update.effective_message.text
    message_text = command_text[len("/" + ADD_PROJECT_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with no arguments, excpected 2"
        )
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text=f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    args: list[str] = message_text.strip().split(" ")

    if len(args) != 2:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with {len(args)} arguments, excpected 2"
        )
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text=f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    language, project_name = args

    if project_name not in PROJECT_NAMES:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with invalid project name '{project_name}' argument"
        )
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Неправильное название проекта (второй аргумент)",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    student_message = update.message.reply_to_message

    bot_reply_text = find_reply_by_language_and_project(language, project_name)

    if bot_reply_text == None:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} for project '{project_name}' and '{language}' didn't find suitable reply"
        )
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Сообщение по заданным критериям не найдено",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    bot_reply_text = bot_reply_text.replace("\\n", "\n")

    projects_reviews_collection_chat_id: str | None = os.getenv(
        "PROJECTS_REVIEWS_COLLECTION_CHAT_ID"
    )

    if projects_reviews_collection_chat_id is None:
        log.error(f"{ADD_PROJECT_COMMAND_NAME} cannot find chat_id to forward message")
        error_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Чат для пересылки не найден",
            reply_to_message_id=update.effective_message.id,
        )
        await asyncio.sleep(10)
        await context.bot.delete_messages(
            chat_id=chat_id,
            message_ids=[update.effective_message.id, error_message.id],
        )
        return

    await context.bot.delete_message(
        chat_id=chat_id,
        message_id=update.effective_message.id,
    )
    await context.bot.forward_message(
        from_chat_id=chat_id,
        chat_id=projects_reviews_collection_chat_id,
        message_id=update.message.reply_to_message.id,
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=bot_reply_text,
        reply_to_message_id=student_message.id,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def is_admin(user: ChatMember) -> bool:
    return (
        user.status == ChatMemberStatus.ADMINISTRATOR
        or user.status == ChatMemberStatus.OWNER
    )


def is_allowed_user(user: ChatMember) -> bool:
    allowed_user_ids = os.getenv("ALLOWED_USER_IDS")

    if allowed_user_ids is None:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} cannot find ALLOWED_USER_IDS to check permissions"
        )
        return False

    allowed_user_ids = allowed_user_ids.split(",")
    allowed_user_ids = list(map(int, allowed_user_ids))

    user_id = user.user.id

    if user_id in allowed_user_ids:
        return True

    return False


def is_reply(message: Message | None) -> bool:
    if message is None:
        return False
    if message.reply_to_message is None:
        return False
    if message.reply_to_message.id == message.reply_to_message.message_thread_id:
        return False
    return True
