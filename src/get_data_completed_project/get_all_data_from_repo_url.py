from env import URL_REPO
from urllib.parse import urlparse
from src.get_data_completed_project.project_data_serializer import ProjectDataSerializer


def get_info_from_url(url: str, lang_project: str, type_project: str) -> ProjectDataSerializer:
    """
    Получаем информацию о репозитории и пользователе из url
        и формируем объект для дальнейшей работы с таблицей.
    :param url: Передаем url репозитория из сообщения.
    :param lang_project: Передаем язык программирования проекта из команды.
    :param type_project: Тип проекта (Виселица, Симуляция и т.п.) из команды
    :return project_data_serializer_obj: Хранит в себе информацию для добавления в таблицу
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")
    # Список содержащий информацию извлеченную из url
    list_path = path.split('/')
    repo_owner = list_path[0]
    repo_name = list_path[1]
    repo_owner_url = f'{parsed_url.scheme}://{parsed_url.hostname}/{repo_owner}'
    # Собираем url репозитория, что бы избежать ошибок и лишних путей
    # (например, что бы избавиться от части пути к конкретному файлу)
    repo_url = f'{parsed_url.scheme}://{parsed_url.hostname}/{repo_owner}/{repo_name}'

    project_data_serializer_obj = ProjectDataSerializer(
        repository_name=repo_name,
        name_owner_repo=repo_owner,
        repository_url=repo_url,
        url_owner_repo=repo_owner_url,
        program_lang_project=lang_project,
        type_project=type_project
    )
    return project_data_serializer_obj


if __name__ == '__main__':
    # Test func
    object_project_data = get_info_from_url(URL_REPO, 'Java', 'Конвертер валют')
    print(
        object_project_data.url_owner_repo,
        object_project_data.repository_url,
        object_project_data.name_owner_repo,
        object_project_data.repository_name,
        object_project_data.program_lang_project,
        object_project_data.type_project
    )
