import os
from dotenv import load_dotenv

load_dotenv()

# Константы для работы с gsheet
JSON_KEY_GOOGLE_API: str | None = os.environ.get("JSON_KEY_GOOGLE_API")
ADD_TO_SHEET_NAME: str | None = os.environ.get("ADD_TO_SHEET_NAME")

# Константы для подключения к БД
POSTGRES_USER: str | None = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD: str | None = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB: str | None = os.environ.get("POSTGRES_DB")
POSTGRES_HOST: str | None = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT: str | None = os.getenv("POSTGRES_PORT")

INTERVIEW_COLLECTION_SPREADSHEET_ID: str | None = os.getenv(
    "INTERVIEW_COLLECTION_SPREADSHEET_ID"
)
SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS: str | None = os.getenv(
    "SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS"
)
