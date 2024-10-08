import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
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
)

from add_project_handler import add_project
from add_project_handler import ADD_PROJECT_COMMAND_NAME

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
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

    await update.inline_query.answer(results)


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
