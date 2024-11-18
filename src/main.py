import logging
from uuid import uuid4

from src.config import logs

from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)
from src.config.env import TELEGRAM_BOT_TOKEN

from src.handler.add_project_handler import add_project
from src.handler.add_project_handler import ADD_PROJECT_COMMAND_NAME

from src.handler.search_interviews_with_question_handler import (
    search_interviews_with_question,
)
from src.handler.search_interviews_with_question_handler import (
    SEARCH_INTERVIEWS_WITH_QUESTION_COMMAND_REGEXP,
)

logs.configure()
log = logging.getLogger(__name__)


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

    assert update.inline_query is not None

    _ = await update.inline_query.answer(results)


if __name__ == "__main__":
    application = (
        ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).concurrent_updates(True).build()
    )

    add_project_handler = CommandHandler(ADD_PROJECT_COMMAND_NAME, add_project)
    search_interviews_with_question_handler = MessageHandler(
        filters.COMMAND & filters.Regex(SEARCH_INTERVIEWS_WITH_QUESTION_COMMAND_REGEXP),
        search_interviews_with_question,
    )
    inline_hello_handler = InlineQueryHandler(hello_inline_query)

    application.add_handler(inline_hello_handler)
    application.add_handler(add_project_handler)
    application.add_handler(search_interviews_with_question_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
