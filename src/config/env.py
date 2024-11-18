import os
from dotenv import load_dotenv

_ = load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Константы для работы с gsheet
JSON_KEY_GOOGLE_API = os.getenv("JSON_KEY_GOOGLE_API")
ADD_TO_SHEET_NAME = os.getenv("ADD_TO_SHEET_NAME")

# Константы для подключения к БД
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

INTERVIEW_COLLECTION_SPREADSHEET_ID = os.getenv("INTERVIEW_COLLECTION_SPREADSHEET_ID")
SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS = os.getenv("SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS")  # fmt: skip

# fmt: off
assert TELEGRAM_BOT_TOKEN is not None, "TELEGRAM_BOT_TOKEN environment variable is not set"

assert JSON_KEY_GOOGLE_API is not None, "JSON_KEY_GOOGLE_API environment variable is not set"
assert ADD_TO_SHEET_NAME is not None, "ADD_TO_SHEET_NAME environment variable is not set"

assert POSTGRES_USER is not None, "POSTGRES_USER environment variable is not set"
assert POSTGRES_PASSWORD is not None, "POSTGRES_PASSWORD environment variable is not set"
assert POSTGRES_DB is not None, "POSTGRES_DB environment variable is not set"
assert POSTGRES_HOST is not None, "POSTGRES_HOST environment variable is not set"
assert POSTGRES_PORT is not None, "POSTGRES_PORT environment variable is not set"

assert INTERVIEW_COLLECTION_SPREADSHEET_ID is not None, "INTERVIEW_COLLECTION_SPREADSHEET_ID environment variable is not set"
assert SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS is not None, "SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS environment variable is not set"
