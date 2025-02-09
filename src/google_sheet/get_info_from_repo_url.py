from urllib.parse import urlparse
from src.google_sheet.dto.project_dto import Project


def get_info_from_url(url: str, lang_project: str, type_project: str) -> Project:
    """
    Получаем информацию о репозитории и пользователе из url
        и формируем объект для дальнейшей работы с таблицей.
    :param url: Передаем url репозитория из сообщения.
    :param lang_project: Передаем язык программирования проекта из команды.
    :param type_project: Передаем тип проекта из команды.
    :return project_data_serializer_obj: Хранит в себе информацию для добавления в таблицу
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")
    # Список содержащий информацию извлеченную из url
    list_path = path.split("/")
    repo_owner = list_path[0]
    repo_name = list_path[1]
    repo_owner_url = f"{parsed_url.scheme}://{parsed_url.hostname}/{repo_owner}"
    # Собираем url репозитория, что бы избежать ошибок и лишних путей
    # (например, что бы избавиться от части пути к конкретному файлу)
    repo_url = f"{parsed_url.scheme}://{parsed_url.hostname}/{repo_owner}/{repo_name}"

    return Project(
        period=None,
        repo_name=repo_name,
        author_name=repo_owner,
        repo_link=repo_url,
        author_link=repo_owner_url,
        language=lang_project,
        project_name=type_project,
    )


if __name__ == "__main__":
    # Test func
    object_project_data = get_info_from_url(
        "Для url репозитория", "Java", "Конвертер валют"
    )
    print(
        object_project_data.author_name,
        object_project_data.repo_link,
        object_project_data.author_link,
        object_project_data.repo_name,
        object_project_data.language,
    )
