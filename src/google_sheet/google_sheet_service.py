# pyright: reportExplicitAny=false

from typing import Any
from urllib.parse import urlparse
import logging

from src.google_sheet import google_sheet_client


from src.google_sheet.dto.interview_question_category_dto import (
    InterviewQuestionCategory,
)
from src.google_sheet.dto.interview_question_dto import InterviewQuestion
from src.google_sheet.dto.interview_question_timestamp_dto import (
    InterviewQuestionTimestamp,
)
from src.google_sheet.dto.interview_info_dto import InterviewInfo

from src.google_sheet.dto.project_dto import Project
from src.google_sheet.dto.review_dto import Review

from src.google_sheet.constants.interview_collection_sheet_constants import (
    QUESTION_COL_INDEX,
    QUESTION_ID_COL_INDEX,
    FIRST_QUESTION_ROW_INDEX,
    INTERVIEW_NAME_ROW_INDEX,
    INTERVIEW_LINK_ROW_INDEX,
    FIRST_INTERVIEW_COL_INDEX,
    QUESTION_POPULRATIY_COL_INDEX,
)

from src.google_sheet.constants.projects_reviews_sheet_constants import (
    CURRENT_PERIOD_COL_INDEX,
    CURRENT_PERIOD_ROW_INDEX,
    FIRST_PROJECT_ROW_INDEX,
    FIRST_REVIEW_ROW_INDEX,
    PROJECT_AUTHOR_LINK_COL_INDEX,
    PROJECT_AUTHOR_NAME_COL_INDEX,
    PROJECT_LANGUAGE_COL_INDEX,
    PROJECT_PROJECT_NAME_COL_INDEX,
    PROJECT_REPO_LINK_COL_INDEX,
    PROJECT_REPO_NAME_COL_INDEX,
    PROJECT_PERIOD_COL_INDEX,
    REVIEW_AUTHOR_NAME_COL_INDEX,
    REVIEW_AUTHOR_TG_LINK_COL_INDEX,
    REVIEW_AUTHOR_TG_NICK_COL_INDEX,
    REVIEW_LANGUAGE_COL_INDEX,
    REVIEW_PERIOD_COL_INDEX,
    REVIEW_PROJECT_NAME_COL_INDEX,
    REVIEW_REPO_LINK_COL_INDEX,
    REVIEW_REVEIW_LINK_COL_INDEX,
    REVIEW_REVIEW_TYPE_COL_INDEX,
)

log = logging.getLogger(__name__)

interview_questions: dict[int, InterviewQuestion] = dict()


def add_project(project_name: str, language: str, link: str):
    parsed_url = urlparse(link)
    author, repo, *_ = parsed_url.path.strip("/").split("/")

    author_url = f"{parsed_url.scheme}://{parsed_url.hostname}/{author}"
    repo_url = f"{parsed_url.scheme}://{parsed_url.hostname}/{author}/{repo}"

    projects_sheet = google_sheet_client.get_projects_sheet(editable=True)

    project_added = (
        projects_sheet.find(repo_url, in_column=PROJECT_REPO_LINK_COL_INDEX + 1)
        is not None
    )

    if project_added:
        raise Exception(
            f"Project '{project_name}' from '{author}' already added to the Google Sheet"
        )

    current_period_cell = projects_sheet.cell(
        CURRENT_PERIOD_ROW_INDEX + 1, CURRENT_PERIOD_COL_INDEX + 1
    )
    current_period = str(current_period_cell.value)

    _ = projects_sheet.append_row(
        [current_period, project_name, language, repo, repo_url, author, author_url]
    )


def get_interview_question_by_id(question_id: int) -> InterviewQuestion | None:
    if len(interview_questions) == 0:
        _update_interview_questions()

    return interview_questions.get(question_id)


def get_interview_questions() -> list[InterviewQuestion]:
    if len(interview_questions) == 0:
        _update_interview_questions()

    return list(interview_questions.values())


def get_projects_data() -> list[Project]:
    log.info("Parsing projects reviews collection Google spreadsheet")

    projects_sheet = google_sheet_client.get_projects_sheet()

    # Col[Row[Any]]
    projects_sheet_values: list[list[Any]] = projects_sheet.get_all_values()

    project_data: list[Project] = []

    for i, row in enumerate(projects_sheet_values):
        if i < FIRST_PROJECT_ROW_INDEX:
            continue

        project_name = row[PROJECT_PROJECT_NAME_COL_INDEX]

        # Is category
        if project_name is None or len(project_name) == 0:
            continue

        period = row[PROJECT_PERIOD_COL_INDEX]
        language = row[PROJECT_LANGUAGE_COL_INDEX]
        repo_name = row[PROJECT_REPO_NAME_COL_INDEX]
        repo_link = row[PROJECT_REPO_LINK_COL_INDEX]
        author_name = row[PROJECT_AUTHOR_NAME_COL_INDEX]
        author_link = row[PROJECT_AUTHOR_LINK_COL_INDEX]

        project_data.append(
            Project(
                period=period,
                project_name=project_name,
                language=language,
                repo_name=repo_name,
                repo_link=repo_link,
                author_name=author_name,
                author_link=author_link,
            )
        )

    return project_data


def get_reviews_data() -> list[Review]:
    log.info("Parsing projects reviews collection Google spreadsheet")

    reviews_sheet = google_sheet_client.get_reviews_sheet()

    # Col[Row[Any]]
    reviews_sheet_values: list[list[Any]] = reviews_sheet.get_all_values()

    review_data: list[Review] = []

    for i, row in enumerate(reviews_sheet_values):
        if i < FIRST_REVIEW_ROW_INDEX:
            continue

        project_name = row[REVIEW_PROJECT_NAME_COL_INDEX]

        # Is category
        if project_name is None or len(project_name) == 0:
            continue

        period = row[REVIEW_PERIOD_COL_INDEX]
        language = row[REVIEW_LANGUAGE_COL_INDEX]
        repo_link = row[REVIEW_REPO_LINK_COL_INDEX]
        review_type = row[REVIEW_REVIEW_TYPE_COL_INDEX]
        review_link = row[REVIEW_REVEIW_LINK_COL_INDEX]
        author_name = row[REVIEW_AUTHOR_NAME_COL_INDEX]
        author_tg_nick = row[REVIEW_AUTHOR_TG_NICK_COL_INDEX]
        author_tg_link = row[REVIEW_AUTHOR_TG_LINK_COL_INDEX]

        review_data.append(
            Review(
                period=period,
                project_name=project_name,
                language=language,
                repo_link=repo_link,
                review_type=review_type,
                review_link=review_link,
                author_name=author_name,
                author_tg_nick=author_tg_nick,
                author_tg_link=author_tg_link,
            )
        )

    return review_data


def _update_interview_questions() -> None:
    log.info("Parsing interview collection Google spreadsheet")

    interviews_sheet = google_sheet_client.get_interviews_sheet()

    # Col[Row[Any]]
    interviews_sheet_values: list[list[Any]] = interviews_sheet.get_all_values()

    question_id_to_row_category = _map_question_id_to_row_category(
        interviews_sheet_values
    )

    col_to_interview_info = _map_col_index_to_interview_info(interviews_sheet_values)

    questions = _map_question_id_to_question(
        question_id_to_row_category, col_to_interview_info
    )

    interview_questions.update(questions)


def _map_question_id_to_row_category(
    cols_rows: list[list[Any]],
) -> dict[int, tuple[list[Any], InterviewQuestionCategory]]:
    """
    Maps question id to question row.

    Question row will not be affected, meaning - question id will be present as the first element in the returned list.

    Example:

    For the following table
    ┌───┬────┬────┬────────┬───────┐
    │ A │  B │  C │    D   │    E  │
    ├───┼────┴────┴────────┴───────┤
    │ l │ Java Core                │
    ├───┼────┬────┬────────┬───────┤
    │ 1 │ q1 │ 1% │ 10:00  │       │
    ├───┼────┼────┼────────┼───────┤
    │ 2 │ q2 │ 2% │        │ 20:00 │
    ├───┼────┴────┴────────┴───────┤
    │ l │ OOP                      │
    ├───┼────┬────┬────────┬───────┤
    │ 3 │ q2 │ 3% │ 30:00  │       │
    └───┴────┴────┴────────┴───────┘

    Function will return this dict
    {
        1 : ([1, q1, 1%, 10:00, ''], Java Core),
        2 : ([2, q2, 2%, '', 20:00], Java Core),
        3 : ([3, q3, 3%, 30:00, ''], OOP),
    }
    """

    q_id_to_q_row: dict[int, tuple[list[Any], InterviewQuestionCategory]] = dict()
    current_category_name = ""
    current_category_link = ""
    current_category_popularity = 0.0

    for i, row in enumerate(cols_rows):
        if i < FIRST_QUESTION_ROW_INDEX - 1:
            continue

        question_id = row[QUESTION_ID_COL_INDEX]

        # Is category
        if _is_link(question_id):
            link = str(question_id)
            name = str(row[QUESTION_COL_INDEX])

            current_category_name = name
            current_category_link = link

            popularity_precents = str(row[QUESTION_POPULRATIY_COL_INDEX])
            popularity = popularity_precents.replace("%", "")

            if popularity == "":
                log.warning(f"Popularity percents for category {name} is not found")
                continue

            current_category_popularity = float(popularity)

            continue

        if not _is_int(question_id):
            continue

        q_id_to_q_row[int(question_id)] = row, InterviewQuestionCategory(
            name=current_category_name,
            link=current_category_link,
            popularity=current_category_popularity,
        )

    return q_id_to_q_row


def _map_col_index_to_interview_info(
    cols_rows: list[list[Any]],
) -> dict[int, InterviewInfo]:
    """
    Maps column index to the InterviewInfo.

    Iterates only over table header, specifically - first rows before the questions and timestamps are appeared

    Example:

    For the following table header
    ┌───┬────────┬────────┬────────┬────────┐
    │ 0 │    1   │    2   │    3   │    4   │  column indices
    ├───┼────────┼────────┼────────┼────────┤
    │ 1 │  vlad  │ sergey │ kostya │  timur │
    ├───┼────────┼────────┼────────┼────────┤
    │ 2 │ link 1 │ link 2 │ link 3 │ link 4 │
    ├───┼────────┼────────┼────────┼────────┤
    │ 3 │        │        │        │        │
    └───┴────────┴────────┴────────┴────────┘

    Function will return this dict
    {
        1 : InterviewInfo(vlad, link 1),
        2 : InterviewInfo(sergey, link 2),
        3 : InterviewInfo(kostya, link 3),
        4 : InterviewInfo(timur, link 4),
    }
    """

    i_to_interview_name: dict[int, str] = dict()
    i_to_interview_link: dict[int, str] = dict()

    for i, row in enumerate(cols_rows):
        # Iterate only through table header
        if i >= FIRST_QUESTION_ROW_INDEX:
            break

        for j, col in enumerate(row):
            # Iterate only through table header
            if j < FIRST_INTERVIEW_COL_INDEX:
                continue

            # Interview name row
            if i == INTERVIEW_NAME_ROW_INDEX:
                interview_name = str(col)

                if len(interview_name) == 0:
                    continue

                i_to_interview_name[j] = interview_name

            # Interview link row
            elif i == INTERVIEW_LINK_ROW_INDEX:
                interview_link = str(col)

                if len(interview_link) == 0:
                    continue

                i_to_interview_link[j] = interview_link

            # Table header ended
            else:
                break

    i_to_interview_info: dict[int, InterviewInfo] = dict()

    if len(i_to_interview_name) != len(i_to_interview_link):
        log.warning(
            "Some interviews don't have links or vice versa in the Google Sheet table"
        )

    # Combine links and names
    for col_index in i_to_interview_link:
        interview_link = i_to_interview_link.get(col_index)
        interview_name = i_to_interview_name.get(col_index)

        if interview_link is None or interview_name is None:
            continue

        i_to_interview_info[col_index] = InterviewInfo(
            name=interview_name, link=interview_link
        )

    return i_to_interview_info


def _map_question_id_to_question(
    question_id_to_row_category: dict[int, tuple[list[Any], InterviewQuestionCategory]],
    col_to_interview_info: dict[int, InterviewInfo],
) -> dict[int, InterviewQuestion]:
    """Maps question id to the IntervewQuestion."""

    id_to_question: dict[int, InterviewQuestion] = dict()

    for question_id in question_id_to_row_category:
        [row, category] = question_id_to_row_category[question_id]

        interview_question = InterviewQuestion(
            question_id, "", 0.0, [], InterviewQuestionCategory("", "", 0.0)
        )

        for i, col in enumerate(row):
            if i == QUESTION_COL_INDEX:
                interview_question.question = str(col)
                continue

            if i == QUESTION_POPULRATIY_COL_INDEX and len(col) > 0:
                popularity_precents = str(col)
                popularity = popularity_precents.replace("%", "")

                if popularity == "":
                    log.warning(
                        f"Popularity percents for question {interview_question.question} is not found"
                    )
                    continue

                interview_question.popularity = float(popularity)
                continue

            if i >= FIRST_INTERVIEW_COL_INDEX and len(col) > 0:
                timestamp = str(col)
                interview_info = col_to_interview_info[i]

                interview_timestamp = InterviewQuestionTimestamp(
                    timestamp, interview_info
                )

                interview_question.timestamps.append(interview_timestamp)

        interview_question.category = category
        id_to_question[question_id] = interview_question

    return id_to_question


def _is_int(x: int | float | str | None | Any) -> bool:
    if isinstance(x, int):
        return True
    try:
        _ = int(x)  # pyright: ignore [reportArgumentType]
        return True
    except Exception:
        return False


def _is_link(x: int | float | str | None | Any) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return x.startswith("http")
    try:
        x_str = str(x)
        return x_str.startswith("http")
    except Exception:
        return False
