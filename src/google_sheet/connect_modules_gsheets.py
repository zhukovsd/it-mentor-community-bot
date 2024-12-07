import logging

from src.config.env import ADDED_PROJECTS_SPREADSHEET_ID, JSON_KEY_GOOGLE_API
from src.config import logs

from src.google_sheet.dto.dto_check_validation_added_data import (
    CheckValidationAddedDataDTO,
)
from src.google_sheet.parse_url_from_message import parse_url_from_message
from src.google_sheet.google_sheet_service import GSheetService
from src.google_sheet.get_info_from_repo_url import get_info_from_url


logs.configure()
log = logging.getLogger(__name__)


def connect_modules_to_add_data_to_gsheets(
    message: str, lang_project: str, type_project: str
) -> CheckValidationAddedDataDTO:
    """
    Подключение модулей для добавления данных в гугл таблицы итогов месяца.
    :param message: Пересланное боту сообщение для добавления.
    :param lang_project: Язык программирования добавляемого проекта. Достается из параметров команды.
    :param type_project: Тип проекта. Должен быть аналогичен итему из списка PROJECT_NAMES.
        Достается из параметров команды.
    :return :
    """
    url = parse_url_from_message(message)

    if url is None:
        error_message = """
Отсутствует ссылка в передаваемом сообщении 
В gsheet ничего не добавлено
        """
        err_object = CheckValidationAddedDataDTO(
            error_message=error_message, boolean_val=False
        )
        log.error(error_message)
        return err_object

    project_data_obj = get_info_from_url(
        url=url, lang_project=lang_project, type_project=type_project
    )

    if ADDED_PROJECTS_SPREADSHEET_ID is None or ADDED_PROJECTS_SPREADSHEET_ID == "":
        error_message = """
Данные в таблицу не могут быть добавлены
Передайте корректное имя таблицы в которую будем добавлять данные
Затем повторите попытку
        """
        err_object = CheckValidationAddedDataDTO(
            error_message=error_message, boolean_val=False
        )
        log.error(error_message)
        return err_object

    add_in_sheets_obj = GSheetService(json_key_google_api=JSON_KEY_GOOGLE_API)
    add_in_sheets_obj.add_project_to_gsheet(
        project_data_object=project_data_obj, gsheets_id=ADDED_PROJECTS_SPREADSHEET_ID
    )
    check_obj = CheckValidationAddedDataDTO()

    return check_obj
