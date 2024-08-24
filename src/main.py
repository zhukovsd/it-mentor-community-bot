import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import (
    ChatMember,
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
)
from telegram.constants import ChatMemberStatus, ParseMode

from repository import find_reply_by_language_and_project

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)

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


async def add_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info(f"{ADD_PROJECT_COMMAND_NAME} was called")

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = await update.get_bot().get_chat_member(chat_id, user_id)

    if not is_admin(user):
        log.error(f"{ADD_PROJECT_COMMAND_NAME} was called by not admin user")
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


async def hello_inline_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="hello world",
            input_message_content=InputTextMessageContent("Hello, World"),
        )
    ]

    await update.inline_query.answer(results)


def is_admin(user: ChatMember) -> bool:
    return (
        user.status == ChatMemberStatus.ADMINISTRATOR
        or user.status == ChatMemberStatus.OWNER
    )


if __name__ == "__main__":
    _ = load_dotenv()

    bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")

    if bot_token is None:
        raise EnvironmentError("'TELEGRAM_BOT_TOKEN' is not present")

    application = ApplicationBuilder().token(bot_token).concurrent_updates(True).build()

    add_project_handler = CommandHandler(ADD_PROJECT_COMMAND_NAME, add_project)
    inline_hello_handler = InlineQueryHandler(hello_inline_query)

    application.add_handler(inline_hello_handler)
    application.add_handler(add_project_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
