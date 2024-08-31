import logging
import os
from telegram import ChatMember, Update
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
    log.info(f"{ADD_PROJECT_COMMAND_NAME} was called")

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = await update.get_bot().get_chat_member(chat_id, user_id)

    if not is_admin(user) and not is_allowed_user(user):
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called by not admin user: {user.user.id}-{user.status}"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У вас нет прав на использование данной команды",
        )
        return

    if update.message.reply_to_message is None:
        log.error(f"{ADD_PROJECT_COMMAND_NAME} was called outside of reply")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сделайте реплай на сообщение со ссылкой на проект",
        )
        return

    command_text = update.message.text
    message_text = command_text[len("/" + ADD_PROJECT_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with no arguments, excpected 2"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
        )
        return

    args: list[str] = message_text.strip().split(" ")

    if len(args) != 2:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with {len(args)} arguments, excpected 2"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
        )
        return

    language, project_name = args

    if project_name not in PROJECT_NAMES:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with invalid project name '{project_name}' argument"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Неправильное название проекта (второй аргумент)",
        )
        return

    student_message = update.message.reply_to_message

    bot_reply_text = find_reply_by_language_and_project(language, project_name)

    if bot_reply_text == None:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} for project '{project_name}' and '{language}' didn't find suitable reply"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сообщение по заданным критериям не найдено",
        )
        return

    bot_reply_text = bot_reply_text.replace("\\n", "\n")

    projects_reviews_collection_chat_id: str | None = os.getenv(
        "PROJECTS_REVIEWS_COLLECTION_CHAT_ID"
    )

    if projects_reviews_collection_chat_id is None:
        log.error(f"{ADD_PROJECT_COMMAND_NAME} cannot find chat_id to forward message")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Чат для пересылки не найден",
        )
        return

    await context.bot.forward_message(
        from_chat_id=update.effective_chat.id,
        chat_id=projects_reviews_collection_chat_id,
        message_id=update.effective_message.id,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
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
