from typing import Any
import gspread
import json
import logging

from log_config import log_config
import env
from .gsheet_dtos import (
    ProjectDataDTO,
    GSheetFieldsDTO,
    InterviewQuestion,
    InterviewQuestionTimestamp,
    InterviewInfo,
)
from .get_info_from_repo_url import get_info_from_url

from .interview_collection_sheet_constants import (
    QUESTION_COL_INDEX,
    SUMMARY_SHEET_INDEX,
    QUESTION_ID_COL_INDEX,
    FIRST_QUESTION_ROW_INDEX,
    INTERVIEW_NAME_ROW_INDEX,
    INTERVIEW_LINK_ROW_INDEX,
    FIRST_INTERVIEW_COL_INDEX,
    QUESTION_POPULRATIY_COL_INDEX,
)

log_config()
log = logging.getLogger(__name__)


class GSheetService:
    def __init__(self, json_key_google_api):
        """
        Нужен для добавления проекта в таблицу итогов
        """
        # Подключение происходит с помощью ключа превращенного в dict
        self.__dict_api_key_gsheet = json.loads(json_key_google_api)
        self.__google_sheet_client = gspread.service_account_from_dict(
            self.__dict_api_key_gsheet
        )
        # Для получения индекса по имени листа, который используется для открытия нужного нам листа
        self.__index_sheet_list = {
            "hangman": 0,
            "simulation": 1,
            "currency-exchange": 2,
            "tennis-scoreboard": 3,
            "weather-viewer": 4,
            "cloud-file-storage": 5,
            "task-tracker": 6,
            "другое": 7,
        }
        self.__interview_questions: dict[int, InterviewQuestion] = dict()

    def add_project_to_gsheet(
        self, project_data_object: ProjectDataDTO, gsheets_name: str
    ):
        """
        Позволяет нам добавить информацию в google sheets по переданному объекту
        :param project_data_object: Информация извлеченная из url с помощью get_info_from_url
        :param gsheets_name: Имя google таблицы
        :return:
        """
        open_table = self.__google_sheet_client.open(gsheets_name)
        data_object = project_data_object

        open_sheet = open_table.get_worksheet(
            self.__index_sheet_list[data_object.type_project]
        )
        # Ищем, существует ли запись с переданным url в таблице
        find_url_repo_in_sheet = open_sheet.find(data_object.repository_url)
        if find_url_repo_in_sheet is None:
            last_filled_row = len(open_sheet.get_all_values())
            empty_row = last_filled_row + 1
            fields_sheet_obj = GSheetFieldsDTO(open_sheet, empty_row)

            # Если ячейка с url пустая - то вся строка гарантированно пустая
            check_cell_sheet = open_sheet.get(fields_sheet_obj.repository_url).first()
            if check_cell_sheet is None:
                # todo: Как вариант код ниже можно переписать диапазонным добавлением
                #  (Например через insert row - который принимает
                #  список с полями data_object в строгом порядке и номер добавляемой строки)
                open_sheet.update_acell(
                    fields_sheet_obj.repository_name, data_object.repository_name
                )
                open_sheet.update_acell(
                    fields_sheet_obj.repository_url, data_object.repository_url
                )
                open_sheet.update_acell(
                    fields_sheet_obj.name_owner_repo, data_object.name_owner_repo
                )
                open_sheet.update_acell(
                    fields_sheet_obj.url_owner_repo, data_object.url_owner_repo
                )
                open_sheet.update_acell(
                    fields_sheet_obj.program_lang_project,
                    data_object.program_lang_project,
                )

                log.info(
                    "Ссылка - : %s добавлена в Таблицу gsheet",
                    data_object.repository_url,
                )
            else:
                log.warning(
                    "В указанной ячейке: %r содержится информация: %r, пожалуйста проверьте целостность таблицы",
                    fields_sheet_obj.repository_url,
                    check_cell_sheet,
                )
        else:
            # todo: Тут возможно надо будет добавить отправку сообщения в телегу
            log.warning(
                "Проект: %r Существует в таблице и находится в ячейке по адресу: %r",
                find_url_repo_in_sheet.value,
                find_url_repo_in_sheet.address,
            )

    def get_interview_question_by_id(self, question_id: int) -> InterviewQuestion:
        if len(self.__interview_questions) == 0:
            self._update_interview_questions()

        return self.__interview_questions[question_id]

    def _update_interview_questions(self) -> None:
        gsheets_client = gspread.auth.service_account_from_dict(
            self.__dict_api_key_gsheet, scopes=gspread.auth.READONLY_SCOPES
        )

        interview_collection_spreadsheet_id = env.INTERVIEW_COLLECTION_SPREADSHEET_ID
        assert (
            interview_collection_spreadsheet_id is not None
        ), "INTERVIEW_COLLECTION_SPREADSHEET_ID environment variable is not set"

        interview_collection_spreadsheet = gsheets_client.open_by_key(
            interview_collection_spreadsheet_id
        )

        summary_sheet = interview_collection_spreadsheet.get_worksheet(
            SUMMARY_SHEET_INDEX
        )

        # Col[Row[Any]]
        summary_sheet_values: list[list[Any]] = summary_sheet.get_all_values()

        question_id_to_row = self._map_question_id_to_row(summary_sheet_values)
        col_to_interview_info = self._map_col_index_to_interview_info(
            summary_sheet_values
        )

        questions = self._map_question_id_to_question(
            question_id_to_row, col_to_interview_info
        )

        self.__interview_questions = questions

    def _map_question_id_to_row(
        self, cols_rows: list[list[Any]]
    ) -> dict[int, list[Any]]:
        """
        Maps question id to question row.

        Question row will not be affected, meaning - question id will be present as the first element in the returned list.

        Example:

        For the following table
        ┌───┬────┬────┬────────┬───────┐
        │ A │  B │  C │    D   │    E  │
        ├───┼────┼────┼────────┼───────┤
        │ 1 │ q1 │ 1% │ 10:00  │       │
        ├───┼────┼────┼────────┼───────┤
        │ 2 │ q2 │ 2% │        │ 20:00 │
        ├───┼────┼────┼────────┼───────┤
        │ 3 │ q2 │ 3% │ 30:00  │       │
        └───┴────┴────┴────────┴───────┘

        Function will return this dict
        {
            1 : [1, q1, 1%, 10:00, ''],
            2 : [2, q2, 2%, '', 20:00],
            3 : [3, q3, 3%, 30:00, ''],
        }
        """

        q_id_to_q_row: dict[int, list[Any]] = dict()

        for i, row in enumerate(cols_rows):
            if i < FIRST_QUESTION_ROW_INDEX:
                continue

            question_id = row[QUESTION_ID_COL_INDEX]

            if not self._is_int(question_id):
                continue

            q_id_to_q_row[int(question_id)] = row

        return q_id_to_q_row

    def _map_col_index_to_interview_info(
        self,
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
        │ 1 │ name_1 │ name_2 │ name_3 │ name_4 │
        ├───┼────────┼────────┼────────┼────────┤
        │ 2 │ link_1 │ link_2 │ link_3 │ link_4 │
        ├───┼────────┼────────┼────────┼────────┤
        │ 3 │        │        │        │        │
        └───┴────────┴────────┴────────┴────────┘

        Function will return this dict
        {
            1 : (name_1, link_1),
            2 : (name_2, link_2),
            3 : (name_3, link_3),
            4 : (name_4, link_4),
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
            log.warn(
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
        self,
        question_id_to_row: dict[int, list[Any]],
        col_to_interview_info: dict[int, InterviewInfo],
    ) -> dict[int, InterviewQuestion]:
        """Maps question id to the IntervewQuestion."""

        id_to_question: dict[int, InterviewQuestion] = dict()

        for question_id in question_id_to_row:
            row = question_id_to_row[question_id]

            interview_question = InterviewQuestion(question_id, "", 0.0, [])

            for i, col in enumerate(row):
                if i == QUESTION_COL_INDEX:
                    interview_question.question = str(col)
                    continue

                if i == QUESTION_POPULRATIY_COL_INDEX and len(col) > 0:
                    popularity_precents = str(col)
                    popularity = popularity_precents.replace("%", "")
                    interview_question.popularity = float(popularity)
                    continue

                if i >= FIRST_INTERVIEW_COL_INDEX and len(col) > 0:
                    timestamp = str(col)
                    interview_info = col_to_interview_info[i]

                    interview_timestamp = InterviewQuestionTimestamp(
                        timestamp, interview_info
                    )

                    interview_question.timestamps.append(interview_timestamp)

            id_to_question[question_id] = interview_question

        return id_to_question

    def _is_int(self, x: int | float | str | None | Any) -> bool:
        if isinstance(x, int):
            return True
        try:
            _ = int(x)
            return True
        except Exception as e:
            return False


if __name__ == "__main__":
    project_object = get_info_from_url("Для url repo", "Java", "currency-exchange")
    add_project_in_sheet_object = GSheetService("api_json_key")
    add_project_in_sheet_object.add_project_to_gsheet(
        project_object, "monthly_results_for_it_mentor"
    )
