import logging
import asyncio
from telegram import ChatMember, Message, Update
from src.config import env
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

from src.config.env import ADD_PROJECT_ALLOWED_USER_IDS
from src.google_sheet.google_sheet_service import GSheetService
from src.handler import util

PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME = "projectsmonthlysummary"

json_google_api_key = env.JSON_KEY_GOOGLE_API

google_sheet_service = GSheetService(json_google_api_key)

log = logging.getLogger(__name__)

PROJECT_RUSSIAN_NAMES = {
    "hangman": "Виселица",
    "simulation": "Симуляция",
    "currency-exchange": "Обмен валют",
    "tennis-scoreboard": "Теннисное табло",
    "weather-viewer": "Погода",
    "cloud-file-storage": "Облачное хранилище файлов",
    "task-tracker": "Планировщик задач",
    "other": "Другое",
}


async def projects_monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), "projectsmonthlysummary command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), "projectsmonthlysummary command should be used by user, it must not be None"
    assert command_message is not None, "add_project command cannot be None"

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

    if not is_admin(chat_member) and not is_allowed_user(chat_member):
        log.error(
            f"{PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME} was called by not admin user: {chat_member.user.id}-{chat_member.status}"
        )
        await reply_with_error("У вас нет прав на использование данной команды")
        return

    command_text = command_message.text

    assert command_text is not None, "Command text cannot be None"

    message_text = command_text[len("/" + PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME} was called with no arguments, expected 1"
        )
        await reply_with_error(
            f"Команда {PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME} должна вызываться с текущим периодом для генерации сообщения в виде параметра"
        )
        return

    period = message_text.strip()

    if len(period) == 0:
        log.error(
            f"{PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME} was called with no argument, excpected 1"
        )
        await reply_with_error(
            f"Команда {PROJECTS_MONTHLY_SUMMARY_COMMAND_NAME} должна вызываться с текущим периодом для генерации сообщения в виде параметра"
        )
        return

    projects = google_sheet_service.get_projects_data()

    if len(projects) == 0:
        log.error(f"No projects found in the Google sheet with projects")
        await reply_with_error("Не найдены проекты в таблице с проектами")
        return

    projects = filter(lambda x: x.period == period, projects)
    projects = sorted(
        projects,
        key=lambda project: list(PROJECT_RUSSIAN_NAMES.keys()).index(
            project.project_name
        ),
    )

    bullets_by_projects: dict[str, list[str]] = {}

    for project in projects:
        bullets = bullets_by_projects.get(project.project_name)

        if bullets is None:
            bullets = []

        bullet = f" • [{util.escape_special_chars(project.repo_name)}]({project.repo_link}) от [{util.escape_special_chars(project.author_name)}]({project.author_link}) на {project.language}"

        bullets.append(bullet)

        bullets_by_projects[project.project_name] = bullets

    project_blocks: list[str] = []

    for project, bullets in bullets_by_projects.items():
        projects_header = f"*{PROJECT_RUSSIAN_NAMES[project]}*"
        projects = "\n".join(bullets)

        project_block = projects_header + "\n\n" + projects

        project_blocks.append(project_block)

    header = f"*Проекты, {period}*"

    project_blocks[0] = header + "\n\n" + project_blocks[0]

    messages = util.compress_messages(project_blocks)

    _ = await context.bot.delete_message(
        chat_id=chat.id,
        message_id=command_message.id,
    )

    for text in messages:
        _ = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            message_thread_id=command_message.message_thread_id,
            disable_web_page_preview=True,
        )
        await asyncio.sleep(1)


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
