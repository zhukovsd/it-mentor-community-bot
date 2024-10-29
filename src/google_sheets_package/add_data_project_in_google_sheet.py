import gspread
from src.env import JSON_KEY_GOOGLE_API
import json
from src.env import URL_REPO
from src.get_data_completed_project_package.project_data_serializer import ProjectDataSerializer
from src.get_data_completed_project_package.get_all_data_from_repo_url import get_info_from_url
from src.google_sheets_package.table_fields_serializer import TableFieldsSerializer


class AddDataProjectInGSheet:
    def __init__(self):
        """
        Нужен для добавления проекта в таблицу итогов
        """
        # Подключение происходит с помощью ключа превращенного в dict
        self.__dict_api_key_gsheet = json.loads(JSON_KEY_GOOGLE_API)
        self.__google_sheet_object = gspread.service_account_from_dict(self.__dict_api_key_gsheet)
        # Для получения индекса по имени листа, который используется для открытия нужного нам листа
        self.__index_sheet_list = {
            "hangman": 0,
            "simulation": 1,
            "currency-exchange": 2,
            "tennis-scoreboard": 3,
            "weather-viewer": 4,
            "cloud-file-storage": 5,
            "task-tracker": 6,
        }

    def add_project_in_gsheet(self, project_data_object: ProjectDataSerializer, gsheets_name: str):
        """
        Позволяет нам добавить информацию в google sheets по переданному объекту
        :param project_data_object: Информация извлеченная из url с помощью get_info_from_url
        :param gsheets_name: Имя google таблицы
        :return:
        """
        open_table = self.__google_sheet_object.open(gsheets_name)
        data_object = project_data_object

        open_sheet = open_table.get_worksheet(self.__index_sheet_list[data_object.type_project])
        # Ищем, существует ли запись с переданным url в таблице
        find_url_repo_in_sheet = open_sheet.find(data_object.repository_url)
        if find_url_repo_in_sheet is None:
            last_filled_row = len(open_sheet.get_all_values())
            empty_row = last_filled_row + 1
            fields_sheet_obj = TableFieldsSerializer(open_sheet, empty_row)

            # Если ячейка с url пустая - то вся строка гарантированно пустая
            check_cell_sheet = open_sheet.get(fields_sheet_obj.repository_url).first()
            if check_cell_sheet is None:
                # todo: Как вариант код ниже можно переписать диапазонным добавлением
                #  (Например через insert row - который принимает
                #  список с полями data_object в строгом порядке и номер добавляемой строки)
                open_sheet.update_acell(fields_sheet_obj.repository_name, data_object.repository_name)
                open_sheet.update_acell(fields_sheet_obj.repository_url, data_object.repository_url)
                open_sheet.update_acell(fields_sheet_obj.name_owner_repo, data_object.name_owner_repo)
                open_sheet.update_acell(fields_sheet_obj.url_owner_repo, data_object.url_owner_repo)
                open_sheet.update_acell(fields_sheet_obj.program_lang_project, data_object.program_lang_project)
            else:
                print(f'В ячейке {fields_sheet_obj.repository_url} содержится {check_cell_sheet}')
        else:
            # todo: Тут возможно надо будет добавить отправку сообщения в телегу
            print(f'{find_url_repo_in_sheet.value} Существует в таблице и находится в {find_url_repo_in_sheet.address}')


if __name__ == '__main__':
    project_object = get_info_from_url(URL_REPO, "Java", "currency-exchange")
    add_project_in_sheet_object = AddDataProjectInGSheet()
    add_project_in_sheet_object.add_project_in_gsheet(project_object, 'monthly_results_for_it_mentor')
