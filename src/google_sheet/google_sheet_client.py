import json
import gspread
from gspread.auth import DEFAULT_SCOPES, READONLY_SCOPES
from gspread.worksheet import Worksheet

from src.config import env
from src.google_sheet.constants.interview_collection_sheet_constants import (
    SUMMARY_SHEET,
)
from src.google_sheet.constants.projects_reviews_sheet_constants import (
    PROJECTS_SHEET,
    REVIEWS_SHEET,
)


service_account_key = json.loads(env.GOOGLE_SERVICE_ACCOUNT_JSON_KEY)


def get_projects_sheet(editable: bool = False) -> Worksheet:
    client = gspread.auth.service_account_from_dict(
        service_account_key,
        scopes=(DEFAULT_SCOPES if editable else READONLY_SCOPES),
    )

    return client.open_by_key(env.PROJECTS_REVIEWS_SPREADSHEET_ID).get_worksheet(
        PROJECTS_SHEET
    )


def get_reviews_sheet(editable: bool = False) -> Worksheet:
    client = gspread.auth.service_account_from_dict(
        service_account_key,
        scopes=(DEFAULT_SCOPES if editable else READONLY_SCOPES),
    )

    return client.open_by_key(env.PROJECTS_REVIEWS_SPREADSHEET_ID).get_worksheet(
        REVIEWS_SHEET
    )


def get_interviews_sheet(editable: bool = False) -> Worksheet:
    client = gspread.auth.service_account_from_dict(
        service_account_key,
        scopes=(DEFAULT_SCOPES if editable else READONLY_SCOPES),
    )

    return client.open_by_key(env.INTERVIEW_COLLECTION_SPREADSHEET_ID).get_worksheet(
        SUMMARY_SHEET
    )
