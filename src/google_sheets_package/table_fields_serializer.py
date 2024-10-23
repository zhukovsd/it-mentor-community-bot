class TableFieldsSerializer:
    def __init__(self, object_opened_sheet, number_row_cell_excel: int | str):
        """
        Для удобного взаимодействия с таблицей, содержит в себе Поля
        формата А1, B2 и т.п.
        :param object_opened_sheet: Текущий Лист gsheet с которым работаем
        :param number_row_cell_excel: Текущий номер ячейки (Строки) в которой находимся
        """
        # Имя листа на котором мы сейчас находимся
        self.name_list_excel_file = object_opened_sheet.title
        # Данные репозитория
        self.repository_name = f'A{number_row_cell_excel}'
        self.repository_url = f'B{number_row_cell_excel}'
        # Данные автора
        self.name_owner_repo = f'C{number_row_cell_excel}'
        self.url_owner_repo = f'D{number_row_cell_excel}'
        # На каком языке написан проект
        self.program_lang_project = f'E{number_row_cell_excel}'
        # Данные ревью (Тип - Заметка или видео, и ссылка на ревью)
        self.type_review = f'F{number_row_cell_excel}'
        self.review_link = f'G{number_row_cell_excel}'
        # Данные автора ревью
        self.name_author_review = f'H{number_row_cell_excel}'
        self.user_name_author_in_telegram = f'I{number_row_cell_excel}'
        self.author_review_link = f'J{number_row_cell_excel}'
