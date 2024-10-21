from github import Github
from github import Auth
from env import API_FGP_GITHUB, URL_REPO
from urllib.parse import urlparse
from src.work_with_github_rest_api.url_serialize import UrlSerialize


def get_repo_info_from_url(url: str):
    """
    Получаем информацию о репозитории из url
    :param url: Передаем url репозитория
    :return owner_and_repo_name_obj: Хранит в себе поля с владельцем репозитория и названием,
        а так же список с другими частями url.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")
    # Список содержащий информацию извлеченную из url
    list_path = path.split('/')
    owner_and_repo_name_obj = UrlSerialize(list_path)
    return owner_and_repo_name_obj


def get_url_author_and_lang_project(user_name_in_github: str, repo_in_github: str):
    """
    Получаем url автора и язык программирования проекта
        c помощью github REST API
    :param user_name_in_github: Имя пользователя github
    :param repo_in_github: Название репозитория
    :return user_url, language_project:
        Ссылка на владельца имени пользователя, Язык проекта
    """
    with Github(auth=Auth.Token(API_FGP_GITHUB)) as __connect_github:
        user_url = __connect_github.get_user(user_name_in_github).html_url
        language_project = __connect_github.get_user(user_name_in_github).get_repo(repo_in_github).language
        __connect_github.close()
        return user_url, language_project


if __name__ == '__main__':
    ow_and_repo_name = get_repo_info_from_url(URL_REPO)
    url_and_lang_result = get_url_author_and_lang_project(ow_and_repo_name.owner_repo,
                                                          ow_and_repo_name.repository_name)
    print(url_and_lang_result)
