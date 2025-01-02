import logging
import asyncio
from telegram import ChatMember, Message, Update
from src.config import env
from src.repository import find_reply_by_language_and_project
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

from src.config.env import ADD_PROJECT_ALLOWED_USER_IDS
from src.google_sheet.connect_modules_gsheets import (
    connect_modules_to_add_data_to_gsheets,
)

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
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), "add_project command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), "add_project command should be used by user, it must not be None"
    assert command_message is not None, "add_project command cannot be None"

    async def reply_with_error(text: str, reply_message_id: int) -> None:
        error_message = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_to_message_id=reply_message_id,
        )
        await asyncio.sleep(10)
        _ = await context.bot.delete_messages(
            chat_id=chat.id,
            message_ids=[command_message.id, error_message.id],
        )
        return

    chat_member = await update.get_bot().get_chat_member(chat.id, chat_member.id)

    if not is_admin(chat_member) and not is_allowed_user(chat_member):
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called by not admin user: {chat_member.user.id}-{chat_member.status}"
        )
        await reply_with_error("У вас нет прав на использование данной команды", command_message.id)
        return

    if not is_reply(update.effective_message):
        log.error(f"{ADD_PROJECT_COMMAND_NAME} was called outside of reply")
        await reply_with_error("Сделайте реплай на сообщение со ссылкой на проект", command_message.id)
        return

    command_text = command_message.text

    assert command_text is not None, "Command text cannot be None"

    message_text = command_text[len("/" + ADD_PROJECT_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with no arguments, excpected 2"
        )
        await reply_with_error(
            f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
            command_message.id
        )
        return

    args: list[str] = message_text.strip().split(" ")

    if len(args) != 2:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with {len(args)} arguments, excpected 2"
        )
        await reply_with_error(
            f"Команда {ADD_PROJECT_COMMAND_NAME} должна вызываться с двумя параметрами - язык проекта и название проекта",
            command_message.id
        )
        return

    language, project_name = args

    if project_name not in PROJECT_NAMES:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} was called with invalid project name '{project_name}' argument"
        )
        await reply_with_error("Неправильное название проекта (второй аргумент)",
                               command_message.id)
        return

    student_message = command_message.reply_to_message

    assert (
        student_message is not None
    ), "Replied to message, i.e. student message with project link cannot be None"

    bot_reply_text = find_reply_by_language_and_project(language, project_name)

    if bot_reply_text is None:
        log.error(
            f"{ADD_PROJECT_COMMAND_NAME} for project '{project_name}' and '{language}' didn't find suitable reply"
        )
        await reply_with_error("Сообщение по заданным критериям не найдено", command_message.id)
        return

    bot_reply_text = bot_reply_text.replace("\\n", "\n")

    projects_reviews_collection_chat_id = env.PROJECTS_REVIEWS_COLLECTION_CHAT_ID

    _ = await context.bot.delete_message(
        chat_id=chat.id,
        message_id=command_message.id,
    )
    _ = await context.bot.forward_message(
        from_chat_id=chat.id,
        chat_id=projects_reviews_collection_chat_id,
        message_id=student_message.id,
    )
    _ = await context.bot.send_message(
        chat_id=chat.id,
        text=bot_reply_text,
        reply_to_message_id=student_message.id,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    if student_message.photo or student_message.video or student_message.document:
        log.info(f'Пересланное сообщение содержит изображение, видео или файл, извлекаем текст.')
        message = student_message.caption
    else:
        message = student_message.text

    assert (
        message is not None
    ), "Replied to message, i.e. student message with project link cannot be None"

    check_add_data = connect_modules_to_add_data_to_gsheets(
        message=message, lang_project=language,
        type_project=project_name, command_check=ADD_PROJECT_COMMAND_NAME
    )

    if check_add_data.boolean_val is False:
        await reply_with_error(check_add_data.error_message, student_message.id)


def is_admin(user: ChatMember) -> bool:
    return (
        user.status == ChatMemberStatus.ADMINISTRATOR
        or user.status == ChatMemberStatus.OWNER
    )


def is_allowed_user(user: ChatMember) -> bool:
    allowed_user_ids = ADD_PROJECT_ALLOWED_USER_IDS.split(",")
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
