import os
from dotenv import load_dotenv

_ = load_dotenv()

# pyright: reportAssignmentType=false

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
PROJECTS_REVIEWS_COLLECTION_CHAT_ID: str = os.getenv("PROJECTS_REVIEWS_COLLECTION_CHAT_ID")  # fmt: skip
ADD_PROJECT_ALLOWED_USER_IDS: str = os.getenv("ADD_PROJECT_ALLOWED_USER_IDS")

# Константы для работы с gsheet
JSON_KEY_GOOGLE_API: str = os.getenv("JSON_KEY_GOOGLE_API")
ADDED_PROJECTS_SPREADSHEET_ID: str | None = os.getenv("ADDED_PROJECTS_SPREADSHEET_ID")

# Константы для подключения к БД
POSTGRES_USER: str = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB: str = os.getenv("POSTGRES_DB")
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")

INTERVIEW_COLLECTION_SPREADSHEET_ID: str = os.getenv("INTERVIEW_COLLECTION_SPREADSHEET_ID")  # fmt: skip
SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS: str = os.getenv("SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS")  # fmt: skip

INTERVIEW_PREP_SITE_REPO_OWNER: str = os.getenv("INTERVIEW_PREP_SITE_REPO_OWNER")
INTERVIEW_PREP_SITE_REPO_NAME: str = os.getenv("INTERVIEW_PREP_SITE_REPO_NAME")

GITHUB_COMMUNITY_BOT_ACCESS_TOKEN: str = os.getenv("GITHUB_COMMUNITY_BOT_ACCESS_TOKEN")

QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS: str = os.getenv("QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS")  # fmt: skip

# fmt: off
assert TELEGRAM_BOT_TOKEN is not None, "TELEGRAM_BOT_TOKEN environment variable is not set"
assert PROJECTS_REVIEWS_COLLECTION_CHAT_ID is not None, "PROJECTS_REVIEWS_COLLECTION_CHAT_ID environment variable is not set"
assert ADD_PROJECT_ALLOWED_USER_IDS is not None, "ADD_PROJECT_ALLOWED_USER_IDS environment variable is not set"

assert JSON_KEY_GOOGLE_API is not None, "JSON_KEY_GOOGLE_API environment variable is not set"
# assert ADDED_PROJECTS_SPREADSHEET_ID is not None, "ADDED_PROJECTS_SPREADSHEET_ID environment variable is not set"

assert POSTGRES_USER is not None, "POSTGRES_USER environment variable is not set"
assert POSTGRES_PASSWORD is not None, "POSTGRES_PASSWORD environment variable is not set"
assert POSTGRES_DB is not None, "POSTGRES_DB environment variable is not set"
assert POSTGRES_HOST is not None, "POSTGRES_HOST environment variable is not set"
assert POSTGRES_PORT is not None, "POSTGRES_PORT environment variable is not set"

assert INTERVIEW_COLLECTION_SPREADSHEET_ID is not None, "INTERVIEW_COLLECTION_SPREADSHEET_ID environment variable is not set"
assert SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS is not None, "SEARCH_INTERVIEW_QUESTIONS_COMMAND_CHAT_IDS environment variable is not set"

assert INTERVIEW_PREP_SITE_REPO_OWNER is not None, "INTERVIEW_PREP_SITE_REPO_OWNER environment variable is not set"
assert INTERVIEW_PREP_SITE_REPO_NAME is not None, "INTERVIEW_PREP_SITE_REPO_NAME environment variable is not set"

assert GITHUB_COMMUNITY_BOT_ACCESS_TOKEN is not None, "GITHUB_COMMUNITY_BOT_ACCESS_TOKEN environment variable is not set"

assert QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS is not None, "QUESTIONS_POPULARITY_UPDATE_ALLOWED_USER_IDS environment variable is not set"
