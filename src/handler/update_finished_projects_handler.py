import asyncio
import logging
from telegram import ChatMember, Message, Update
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

from src.config import env
from src.config.env import ADD_PROJECT_ALLOWED_USER_IDS
from src.github import github_service
from src.google_sheet.google_sheet_service import GSheetService
from src import template_service
from src.handler import util
from src.project_with_review_dto import ProjectWithReview

UPDATE_FINISHED_PROJECTS_COMMAND = "updatefinishedprojects"

json_google_api_key = env.JSON_KEY_GOOGLE_API

google_sheet_service = GSheetService(json_google_api_key)

log = logging.getLogger(__name__)
log.level = logging.DEBUG


async def update_finished_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), f"{UPDATE_FINISHED_PROJECTS_COMMAND} command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), f"{UPDATE_FINISHED_PROJECTS_COMMAND} command should be used by user, it must not be None"
    assert (
        command_message is not None
    ), f"{UPDATE_FINISHED_PROJECTS_COMMAND} command cannot be None"

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
            f"{UPDATE_FINISHED_PROJECTS_COMMAND} was called by not admin user: {chat_member.user.id}-{chat_member.status}"
        )
        await reply_with_error("У вас нет прав на использование данной команды")
        return

    projects = google_sheet_service.get_projects_data()
    reviews = google_sheet_service.get_reviews_data()

    if len(projects) == 0:
        log.error(f"No projects found in the Google sheet with projects")
        await reply_with_error("Не найдены проекты в таблице с проектами")
        return

    if len(reviews) == 0:
        log.error(f"No reviews found in the Google sheet with projects")
        await reply_with_error("Не найдены ревью в таблице с проектами")
        return

    projects_with_reviews: list[ProjectWithReview] = []

    for project in projects:
        project_reviews = list(
            filter(lambda r: r.repo_link == project.repo_link, reviews)
        )

        assert project.period is not None

        project_with_review = ProjectWithReview(
            period=project.period,
            project_name=project.project_name,
            language=project.language,
            repo_name=project.repo_name,
            repo_link=project.repo_link,
            author_name=project.author_name,
            author_link=project.author_link,
            reviews=project_reviews,
        )

        projects_with_reviews.append(project_with_review)

    try:
        java_repo_pr = github_service.update_java_projects(projects_with_reviews)

        log.info(java_repo_pr)

        _ = await context.bot.delete_message(
            chat_id=chat.id,
            message_id=command_message.id,
        )

        _ = await context.bot.send_message(
            chat_id=chat.id,
            text=f"PR: {util.escape_special_chars(java_repo_pr)}",
            parse_mode=ParseMode.MARKDOWN_V2,
            message_thread_id=command_message.message_thread_id,
            disable_web_page_preview=True,
        )

    except Exception as e:
        await reply_with_error(str(e))


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
