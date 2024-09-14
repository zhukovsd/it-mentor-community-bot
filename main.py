import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="World")


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
    load_dotenv()

    bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")

    if None:
        raise EnvironmentError("'TELEGRAM_BOT_TOKEN' is not present")

    application = ApplicationBuilder().token(bot_token).concurrent_updates(True).build()

    hello_handler = CommandHandler("hello", hello)
    inline_hello_handler = InlineQueryHandler(hello_inline_query)

    application.add_handler(hello_handler)
    application.add_handler(inline_hello_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
