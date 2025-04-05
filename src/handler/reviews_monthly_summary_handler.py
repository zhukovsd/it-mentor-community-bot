import logging
import asyncio
from telegram import ChatMember, Message, Update
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

from src.config.env import ADD_PROJECT_ALLOWED_USER_IDS
from src.google_sheet import google_sheet_service
from src.handler import util

REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME = "reviewsmonthlysummary"


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


async def reviews_monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), "reviewsmonthlysummary command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), "reviewsmonthlysummary command should be used by user, it must not be None"
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
            f"{REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME} was called by not admin user: {chat_member.user.id}-{chat_member.status}"
        )
        await reply_with_error("У вас нет прав на использование данной команды")
        return

    command_text = command_message.text

    assert command_text is not None, "Command text cannot be None"

    message_text = command_text[len("/" + REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME} was called with no arguments, expected 1"
        )
        await reply_with_error(
            f"Команда {REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME} должна вызываться с текущим периодом для генерации сообщения в виде параметра"
        )
        return

    period = message_text.strip()

    if len(period) == 0:
        log.error(
            f"{REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME} was called with no argument, excpected 1"
        )
        await reply_with_error(
            f"Команда {REVIEWS_MONTHLY_SUMMARY_COMMAND_NAME} должна вызываться с текущим периодом для генерации сообщения в виде параметра"
        )
        return

    reviews = google_sheet_service.get_reviews_data()

    if len(reviews) == 0:
        log.error(f"No reviews found in the Google sheet with projects")
        await reply_with_error("Не найдены ревью в таблице с проектами")
        return

    reviews = list(filter(lambda x: x.period == period, reviews))

    if len(reviews) == 0:
        log.error(
            f"No reviews found in the Google sheet with projects for period {period}"
        )
        await reply_with_error(
            f"Ревью за период {period} не найдены в таблице с проектами"
        )
        return

    reviews = sorted(
        reviews,
        key=lambda project: list(PROJECT_RUSSIAN_NAMES.keys()).index(
            project.project_name
        ),
    )

    bullets_by_project_name: dict[str, list[str]] = {}

    for project in reviews:
        bullets = bullets_by_project_name.get(project.project_name)

        if bullets is None:
            bullets = []

        repo_name = util.escape_special_chars(get_repo_name(project.repo_link))
        author = util.escape_special_chars(get_author_name(project.repo_link))
        author_link = get_author_link(project.repo_link)
        reviewer = util.escape_special_chars(project.author_name)
        reviewer_tg_nick = util.escape_special_chars(project.author_tg_nick)

        bullet = f" • [{repo_name}]({project.repo_link}) от [{author}]({author_link}) на {project.language}, [ревью]({project.review_link}) от {reviewer} [{reviewer_tg_nick}]({project.author_tg_link})"

        bullets.append(bullet)

        bullets_by_project_name[project.project_name] = bullets

    review_blocks: list[str] = []

    for project, bullets in bullets_by_project_name.items():
        reviews_header = f"*{PROJECT_RUSSIAN_NAMES[project]}*"
        reviews = "\n".join(bullets)

        review_block = reviews_header + "\n\n" + reviews

        review_blocks.append(review_block)

    header = f"*Ревью, {period}*"

    review_blocks[0] = header + "\n\n" + review_blocks[0]

    messages = util.compress_messages(review_blocks)

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


def get_author_link(repo_link: str) -> str:
    parts = repo_link.split("/")
    return "/".join(parts[: len(parts) - 1])


def get_author_name(repo_link: str) -> str:
    return repo_link.split("/")[-2]


def get_repo_name(repo_link: str) -> str:
    return repo_link.split("/")[-1]
