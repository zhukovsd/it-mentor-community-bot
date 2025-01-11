import asyncio
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.google_sheet.dto.interview_question_category_dto import (
    InterviewQuestionCategory,
)
from src.google_sheet.dto.interview_question_dto import InterviewQuestion
from src.google_sheet.google_sheet_service import GSheetService
from src.config import env
from src.handler import util

INTERVIEW_QUESTIONS_LIST_COMMAND = "interviewprepquestionslist"

log = logging.getLogger(__name__)

json_google_api_key = env.JSON_KEY_GOOGLE_API

google_sheet_service = GSheetService(json_google_api_key)


async def list_interview_questions_messages(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat = update.effective_chat
    command_message = update.effective_message

    assert chat is not None, "Chat in which command is called cannot be None"
    assert command_message is not None, "Message that triggered bot cannot be None"

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

    if not is_allowed_chat(chat.id):
        log.error(
            f"{INTERVIEW_QUESTIONS_LIST_COMMAND} was called outside of allowed chats, in chat: {chat.effective_name}"
        )
        await reply_with_error("Команда запрещена в этом чате")
        return

    command_text = command_message.text

    assert command_text is not None, "Command text cannot be None"

    message_text = command_text[len("/" + INTERVIEW_QUESTIONS_LIST_COMMAND) :]

    if len(message_text.strip()) == 0:
        log.error(
            f"{INTERVIEW_QUESTIONS_LIST_COMMAND} was called with no argument, excpected 1"
        )
        await reply_with_error(
            f"Команда {INTERVIEW_QUESTIONS_LIST_COMMAND} должна вызываться с boolean параметром"
        )
        return

    args: list[str] = message_text.strip().split(" ")

    if len(args) != 1:
        log.error(
            f"{INTERVIEW_QUESTIONS_LIST_COMMAND} was called with {len(args)} arguments, excpected 1"
        )
        await reply_with_error(
            f"Команда {INTERVIEW_QUESTIONS_LIST_COMMAND} должна вызываться с boolean параметром"
        )
        return

    generate_q_command = to_bool(args[0])

    if generate_q_command is None:
        log.error(
            f"{INTERVIEW_QUESTIONS_LIST_COMMAND} was called with non bool argument {generate_q_command}"
        )
        await reply_with_error(
            f"Команда {INTERVIEW_QUESTIONS_LIST_COMMAND} должна вызываться с boolean параметром"
        )
        return

    interview_questions = google_sheet_service.get_interview_questions()

    category_to_question = split_by_categories(interview_questions)

    messages: list[str] = list()

    for category in category_to_question.keys():
        questions = category_to_question[category]

        message = generate_message(category, questions, generate_q_command)

        messages.append(message)

    log.debug(f"Messages before compressing: {len(messages)}")

    messages = util.compress_messages(messages)

    log.debug(f"Messages after compressing: {len(messages)}")

    for text in messages:
        _ = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        await asyncio.sleep(1)


def is_allowed_chat(chat_id: int) -> bool:
    allowed_chat_ids = env.SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS
    allowed_chat_ids = allowed_chat_ids.split(",")
    allowed_chat_ids = list(map(int, allowed_chat_ids))

    if chat_id in allowed_chat_ids:
        return True

    return False


def to_bool(x: str) -> bool | None:
    x = x.lower()

    if x == "true":
        return True
    if x == "false":
        return False


def split_by_categories(
    questions: list[InterviewQuestion],
) -> dict[InterviewQuestionCategory, list[InterviewQuestion]]:
    category_to_question: dict[InterviewQuestionCategory, list[InterviewQuestion]] = (
        dict()
    )

    for question in questions:
        category = question.category

        questions_in_category = category_to_question.get(category, list())

        questions_in_category.append(question)

        category_to_question[category] = questions_in_category

    return category_to_question


def generate_message(
    category: InterviewQuestionCategory,
    questions: list[InterviewQuestion],
    generate_q_command: bool,
) -> str:
    message_header = f"[{util.escape_special_chars(category.name)}]({category.link})"

    question_bullets: list[str] = list()

    for question in questions:
        text = util.escape_special_chars(question.question)
        popularity = util.escape_special_chars(f"{question.popularity}%")

        question_bullet = f"\\- {text} \\[{popularity}\\]"

        if generate_q_command:
            question_bullet += f" /q{question.id}"

        question_bullets.append(question_bullet)

    message_body = "\n".join(question_bullets)

    message = message_header + "\n\n" + message_body

    assert (
        len(message) < util.MAX_MESSAGE_LENGTH
    ), "Rest of the code assumes that all questions of the category will fit into one telegram message"

    return message
