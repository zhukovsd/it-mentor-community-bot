class GSheetFieldsDTO:
    def __init__(self, object_opened_sheet, number_row_cell_excel: int | str):
        """
        Для удобного взаимодействия с таблицей, содержит в себе Поля
        формата А1, B2 и т.п.
        :param object_opened_sheet: Текущий Лист gsheet с которым работаем
        :param number_row_cell_excel: Текущий номер ячейки (Строки) в которой находимся
        """
        # Имя листа на котором мы сейчас находимся
        self.name_list_excel_file = object_opened_sheet.title
        # Период добавляемый
        self.date_added_project = f'A{number_row_cell_excel}'
        # Тип проекта (hangman, simulation и т.п.) и язык
        self.type_project = f'B{number_row_cell_excel}'
        self.program_lang_project = f"C{number_row_cell_excel}"
        # Информация о репозитории
        self.repository_name = f"D{number_row_cell_excel}"
        self.repository_url = f"E{number_row_cell_excel}"
        # Информация о авторе
        self.name_owner_repo = f"F{number_row_cell_excel}"
        self.url_owner_repo = f"G{number_row_cell_excel}"
