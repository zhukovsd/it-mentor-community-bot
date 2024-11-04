from .parse_url_from_message import parse_url_from_message
from .google_sheet_service import GSheetService
from .get_all_data_from_repo_url import get_info_from_url
from env import ADD_TO_SHEET


def connect_modules_to_add_data_to_gsheets(message: str, lang_project: str, type_project: str):
    """
    Подключение модулей для добавления данных в гугл таблицы итогов месяца.
    :param message: Пересланное боту сообщение для добавления.
    :param lang_project: Язык программирования добавляемого проекта. Достается из параметров команды.
    :param type_project: Тип проекта. Должен быть аналогичен итему из списка PROJECT_NAMES.
        Достается из параметров команды.
    """
    url = parse_url_from_message(message)

    if url is None:
        return

    project_data_obj = get_info_from_url(
        url=url,
        lang_project=lang_project,
        type_project=type_project
    )
    add_in_sheets_obj = GSheetService()
    add_in_sheets_obj.add_project_to_gsheet(
        project_data_object=project_data_obj,
        gsheets_name=ADD_TO_SHEET
    )
