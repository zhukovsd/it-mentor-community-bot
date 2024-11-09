import logging
import re
from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from google_sheets_package.gsheet_dtos import InterviewQuestion
from google_sheets_package import GSheetService
import env

SEARCH_INTERVIEWS_WITH_QUESTION_COMMAND_REGEXP = "q\\d+"

log = logging.getLogger(__name__)

json_google_api_key = env.JSON_KEY_GOOGLE_API
assert (
    json_google_api_key is not None
), "JSON_KEY_GOOGLE_API environment variable is not set"

google_sheet_service = GSheetService(json_google_api_key)

special_chars = [
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
]


async def search_interviews_with_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    assert (
        update.effective_chat is not None
    ), "Chat in which command is called cannot be None"
    assert (
        update.effective_message is not None
    ), "Message that triggered bot cannot be None"
    assert (
        update.effective_message.text is not None
    ), "Message text in command cannot be None"

    question_id = get_question_id(update.effective_message)

    if question_id <= 0:
        _ = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Id вопросов начинаются с единицы",
            reply_to_message_id=update.effective_message.id,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    question = google_sheet_service.get_interview_question_by_id(question_id)

    answers = "\n".join(get_answers(question, 5))

    if len(answers) == 0:
        _ = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="В коллекции собеседований нет ответов на этот вопрос",
            reply_to_message_id=update.effective_message.id,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    response_header = f"Ответы на вопрос \\#{question_id}: `{escape_special_chars(question.question)}` ({question.popularity}%) из коллекции собеседований:\n\n"

    response = response_header + answers

    log.info(response)

    _ = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        reply_to_message_id=update.effective_message.id,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def get_answers(question: InterviewQuestion, amount: int) -> list[str]:
    answers: list[str] = []

    for timestamp in question.timestamps:
        if len(answers) >= amount:
            break

        name = escape_special_chars(timestamp.interview.name)
        link = timestamp.interview.link
        timestamp_text = escape_special_chars(timestamp.timestamp)

        answers.append(f"\\- [{name}]({link}) {timestamp_text}")

    return answers


def escape_special_chars(text: str) -> str:
    pattern = "[" + re.escape("".join(special_chars)) + "]"

    escaped_text = re.sub(pattern, r"\\\g<0>", text)

    return escaped_text


def get_question_id(message: Message) -> int:
    assert message.text is not None

    match = re.search(r"\d+", message.text)

    assert (
        match is not None
    ), "Question id absent in user message. This must not happen as the python-telegram-bot handler shouldn't be triggered if the /q command don't have any digits after it"

    return int(match.group())
