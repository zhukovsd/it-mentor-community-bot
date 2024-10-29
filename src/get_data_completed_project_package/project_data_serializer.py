class ProjectDataSerializer:
    def __init__(self, name_owner_repo, url_owner_repo,
                 repository_name, repository_url,
                 program_lang_project, type_project):
        """
        Хранит корректные данные из url для дальнейшей работы с таблицами
        :param repository_name: Проект/Имя репозитория
        :param name_owner_repo: Имя владельца репозитория
        :param repository_url: Ссылка на репозиторий
        :param url_owner_repo: Ссылка на владельца репозитория
        :param program_lang_project: Язык программирования проекта
        :param type_project: Тип проекта ( "hangman", "simulation",
            "currency-exchange", "tennis-scoreboard",
            "weather-viewer", "cloud-file-storage", "task-tracker")
        """
        self.repository_name = repository_name
        self.name_owner_repo = name_owner_repo
        self.repository_url = repository_url
        self.url_owner_repo = url_owner_repo
        self.program_lang_project = program_lang_project
        self.type_project = type_project
